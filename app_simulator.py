from datetime import datetime
import os
import time
import gspread
from groq import Groq
from google.oauth2.service_account import Credentials
import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Business Pitch Evaluator - Prodi Manajemen",
    page_icon="🦅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Custom CSS UI
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 2rem 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { font-size: 1rem; opacity: 0.9; }

    .eval-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .cta-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px dashed #2563eb;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 2rem;
    }
    .cta-button {
        display: inline-block;
        background-color: #2563eb;
        color: white !important;
        font-weight: bold;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        text-decoration: none;
        margin-top: 1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "response" not in st.session_state:
    st.session_state.response = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Header Hero Banner dengan Tampilan Bersih
st.markdown('<div class="hero-container">', unsafe_allow_html=True)

# Tampilkan gambar logo/maskot dengan st.image jika ada file lokal, atau fallback emoji gagah
if os.path.exists("logo.png"):
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.image("logo.png", width=120)
elif os.path.exists("logo.jpg"):
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.image("logo.jpg", width=120)
else:
    st.markdown(
        '<div style="font-size: 3.5rem; margin-bottom: 0.5rem;">🦅</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
        <div class="hero-title">Student Business Simulator</div>
        <div class="hero-subtitle">Uji & Evaluasi Ide Bisnismu Bersama AI Konsultan dari <b>Prodi Manajemen</b></div>
    </div>
""",
    unsafe_allow_html=True,
)

api_key = st.secrets.get("GROQ_API_KEY")


# Fungsi Simpan ke Google Sheets
def save_to_google_sheets(
    nama, no_hp, sekolah, nama_bisnis, kategori, deskripsi, hasil
):
    try:
        gcp_secrets = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            gcp_secrets, scopes=scopes
        )
        client = gspread.authorize(credentials)
        sheet = client.open("Data Leads Business Simulator").sheet1

        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            waktu,
            nama,
            f"'{no_hp}",
            sekolah,
            nama_bisnis,
            kategori,
            deskripsi,
            hasil[:300],
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Gagal simpan ke Google Sheets: {e}")
        return False


# Form Input
st.markdown("### 📝 Masukkan Data & Ide Bisnismu")

with st.form("business_form"):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Calon Mahasiswa", placeholder="Misal: Andi")
    with col2:
        no_hp = st.text_input(
            "Nomor WhatsApp / HP", placeholder="Misal: 081234567890"
        )

    sekolah = st.text_input(
        "Asal Sekolah / Instansi", placeholder="Misal: SMAN 1 Jakarta"
    )

    nama_bisnis = st.text_input(
        "Nama Ide Bisnis", placeholder="Misal: Donat Kentang Yummy"
    )

    kategori = st.selectbox(
        "Kategori Bisnis",
        [
            "Kuliner (F&B)",
            "Fashion & Beauty",
            "Teknologi / Startup Digital",
            "Jasa & Kreatif",
            "Agribisnis & Lingkungan",
            "Lainnya",
        ],
    )

    deskripsi = st.text_area(
        "Jelaskan Ide Bisnismu Secara Singkat (Maks. 200 Karakter)",
        placeholder=(
            "Contoh: Jual donat kentang lembut varian matcha harga Rp5.000."
            " Target teman sekolah via kantin dan TikTok."
        ),
        max_chars=200,
        height=100,
    )

    submit_btn = st.form_submit_button(
        "⚡ Analisis Ide Bisnis Sekarang", type="primary", use_container_width=True
    )

# Proses AI
if submit_btn:
    if not nama or not no_hp or not nama_bisnis or not deskripsi:
        st.warning(
            "⚠️ Mohon lengkapi Nama, No. WhatsApp, Nama Bisnis, dan Penjelasan"
            " Ide Bisnis dulu ya!"
        )
    elif not api_key:
        st.error("⚠️ API Key belum terpasang di Streamlit Secrets.")
    else:
        prompt = (
            f"Kamu Dosen Pakar Manajemen Pemasaran. Analisis ide bisnis dari"
            f" calon mahasiswa bernama {nama} ({sekolah}).\n"
            f"Detail Bisnis:\n- Nama Bisnis: {nama_bisnis}\n- Kategori:"
            f" {kategori}\n- Deskripsi Ide: {deskripsi}\n\nATURAN: Jawab"
            " SINGKAT, PADAT, dan Maksimal 1-2 kalimat per poin agar jawaban"
            " lengkap dan tidak terpotong!\n\n🎯 **Skor Potensi**: [Nilai"
            " 60-95] - [1 kalimat kesimpulan]\n\n📌 **Rekomendasi STP**:\n-"
            " **Segmenting**: [1 kalimat ringkas]\n- **Targeting**: [1 kalimat"
            " ringkas]\n- **Positioning**: [1 kalimat ringkas]\n\n🛍️ **Bauran"
            " Pemasaran (4P)**:\n- **Product**: [1 saran ringkas]\n- **Price**:"
            " [1 saran ringkas]\n- **Place**: [1 saran ringkas]\n- **Promotion**:"
            " [1 ide promosi sosmed]\n\n🎓 **Pesan Motivasi**: [1-2 kalimat"
            " inspiratif dan ajakan bergabung dengan Prodi Manajemen]"
        )

        try:
            client = Groq(api_key=api_key)

            with st.spinner("🧠 AI sedang menganalisis strategi bisnismu..."):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    max_tokens=500,
                    temperature=0.6,
                )
                res_text = chat_completion.choices[0].message.content

            save_to_google_sheets(
                nama, no_hp, sekolah, nama_bisnis, kategori, deskripsi, res_text
            )

            st.session_state.analyzed = True
            st.session_state.response = res_text
            st.session_state.user_data = {
                "nama": nama,
                "sekolah": sekolah,
                "nama_bisnis": nama_bisnis,
            }
            st.balloons()

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# Tampilan Hasil Evaluasi
if st.session_state.analyzed:
    st.markdown(
        f"""
        <div class="eval-card">
            <h3 style="color: #1e3a8a; margin-top:0;">📊 Analisis Strategi Bisnis: {st.session_state.user_data.get('nama_bisnis')}</h3>
            <p><b>Calon Innovator:</b> {st.session_state.user_data.get('nama')} ({st.session_state.user_data.get('sekolah')})</p>
            <hr>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(st.session_state.response)

    st.markdown(
        """
        <div class="cta-box">
            <h3 style="color: #1e3a8a; margin-bottom: 0.5rem;">🎓 Ingin Ide Bisnis Ini Jadi Nyata?</h3>
            <p style="color: #475569; font-size: 0.95rem;">
                Di <b>Prodi Manajemen</b>, kamu akan dibimbing langsung oleh dosen ahli dan praktisi bisnis untuk mengeksekusi ide ini hingga menghasilkan profit nyata!
            </p>
            <a href="https://wa.me/6281234567890" target="_blank" class="cta-button">
                📲 Konsultasi Pendaftaran via WhatsApp
            </a>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Uji Ide Bisnis Lain / Reset Form", use_container_width=True):
        st.session_state.analyzed = False
        st.session_state.response = ""
        st.session_state.user_data = {}
        st.rerun()

# Footer
st.markdown(
    """
    <br><hr>
    <div style="text-align: center; color: #94a3b8; font-size: 0.8rem;">
        © 2026 <b>Program Studi Manajemen</b> • Student Business Simulator AI
    </div>
""",
    unsafe_allow_html=True,
)
