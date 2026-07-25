from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.oauth2.service_account import Credentials
import gspread
from groq import Groq

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app)


# Fungsi untuk simpan data ke Google Sheets
def append_to_google_sheet(
    nama, no_hp, sekolah, nama_bisnis, kategori, deskripsi, hasil_analisis
):
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        service_account_file = os.getenv(
            "SERVICE_ACCOUNT_FILE", "service_account.json"
        )

        if not os.path.exists(service_account_file):
            print(
                f"Error: File '{service_account_file}' tidak ditemukan!"
            )
            return False

        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        client = gspread.authorize(credentials)

        sheet_name = os.getenv(
            "GOOGLE_SHEET_NAME", "Data Leads Business Simulator"
        )
        sheet = client.open(sheet_name).sheet1

        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            waktu,
            nama,
            f"'{no_hp}",
            sekolah,
            nama_bisnis,
            kategori,
            deskripsi,
            hasil_analisis,
        ]

        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Error simpan ke Google Sheets: {e}")
        return False


# Endpoint Cek Status Server
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "Backend Business Simulator - Universitas Karangturi",
    })


# Endpoint Analisis Bisnis
@app.route("/api/analyze", methods=["POST"])
def analyze_business():
    data = request.get_json()

    required_fields = [
        "nama",
        "no_hp",
        "sekolah",
        "nama_bisnis",
        "kategori",
        "deskripsi",
    ]
    for field in required_fields:
        if not data or not data.get(field):
            return (
                jsonify({
                    "status": "error",
                    "message": f"Field '{field}' wajib diisi!",
                }),
                400,
            )

    nama = data.get("nama")
    no_hp = data.get("no_hp")
    sekolah = data.get("sekolah")
    nama_bisnis = data.get("nama_bisnis")
    kategori = data.get("kategori")
    deskripsi = data.get("deskripsi")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return (
            jsonify({
                "status": "error",
                "message": "GROQ_API_KEY belum dikonfigurasi!",
            }),
            500,
        )

    prompt = f"""Kamu Dosen Pakar Manajemen Pemasaran Universitas Karangturi Semarang. Analisis ide bisnis dari calon mahasiswa bernama {nama} ({sekolah}).

Detail Bisnis:
- Nama Bisnis: {nama_bisnis}
- Kategori: {kategori}
- Deskripsi Ide: {deskripsi}

ATURAN: Jawab SINGKAT, PADAT, dan Maksimal 1-2 kalimat per poin!

🎯 **Skor Potensi**: [Nilai 60-95] - [1 kalimat kesimpulan]

📌 **Rekomendasi STP**:
- **Segmenting**: [1 kalimat ringkas]
- **Targeting**: [1 kalimat ringkas]
- **Positioning**: [1 kalimat ringkas]

🛍️ **Bauran Pemasaran (4P)**:
- **Product**: [1 saran ringkas]
- **Price**: [1 saran ringkas]
- **Place**: [1 saran ringkas]
- **Promotion**: [1 ide promosi sosmed]

🎓 **Pesan Motivasi**: [1-2 kalimat inspiratif dan ajakan bergabung dengan Prodi Manajemen Universitas Karangturi Semarang]"""

    try:
        client = Groq(api_key=groq_api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=500,
            temperature=0.6,
        )

        hasil_analisis = chat_completion.choices[0].message.content

        saved_to_sheets = append_to_google_sheet(
            nama, no_hp, sekolah, nama_bisnis, kategori, deskripsi, hasil_analisis
        )

        return (
            jsonify({
                "status": "success",
                "message": "Analisis berhasil dibuat!",
                "data": {
                    "nama": nama,
                    "sekolah": sekolah,
                    "nama_bisnis": nama_bisnis,
                    "hasil_analisis": hasil_analisis,
                    "saved_to_sheets": saved_to_sheets,
                },
            }),
            200,
        )

    except Exception as e:
        return (
            jsonify({
                "status": "error",
                "message": f"Gagal memproses analisis AI: {str(e)}",
            }),
            500,
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
