from datetime import datetime
import os
import time
import requests
from groq import Groq
import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Business Pitch Evaluator - Prodi Manajemen Universitas Karangturi",
    page_icon="🚀",
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
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .hero-icon {
        font-size: 3.2rem;
        line-height: 1;
        margin-bottom: 0.8rem;
        display: inline-block;
        filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.3));
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .hero-subtitle { 
        font-size: 1rem; 
        color: #e2e8f0;
        opacity: 0.95; 
        font-weight: 400;
    }

    .eval-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
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

# --- HEADER HERO BANNER ---
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-icon">🚀</div>
        <div class="hero-title">Student Business Simulator</div>
        <div class="hero-subtitle">Uji & Evaluasi Ide Bisnismu Bersama AI Konsultan dari <b>Prodi Manajemen Universitas Karangturi</b></div>
    </div>
""",
    unsafe_allow_html=True,
)

api_key = st.secrets.get("GROQ_API_KEY")


# Fungsi Simpan Data ke Google Sheets via Google Forms
def save_to_google_sheets(
    nama, no_hp, sekolah, nama_bisnis, kategori, deskripsi, hasil
):
    try:
        # Link pengiriman form (Response URL)
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdpNOnwOqXv2WlK88yL2X_1Y8M8fG7RzL5P_x8A/formResponse" # Ganti ID Form jika perlu
        
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mapping entry ID dari Google Form
        payload = {
            "entry.1706988008": waktu,
            "entry.977874194": nama,
            "entry.1247992411": f"'{no_hp}",
            "entry.388531157": sekolah,
            "entry.1786925872": nama_bisnis,
            # Tambahkan entry ID sisanya di bawah jika ada
        }
        
        # Kirim data HTTP POST
        requests.post("https://docs.google.com/forms/u/0/d/e/1FAIpQLSc-PLACEHOLDER/formResponse", data=payload)
        return True
    except Exception as e:
        print(f"Gagal simpan ke Google Forms: {e}")
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
        "Asal Sekolah / Instansi", placeholder="Misal: SMAN 1 Semarang"
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
            f"Kamu Dosen Pakar Manajemen Pemasaran Universitas Karangturi"
            f" Semarang. Analisis ide bisnis dari calon mahasiswa bernama {nama}"
            f" ({sekolah}).\nDetail Bisnis:\n- Nama Bisnis: {nama_bisnis}\n-"
            f" Kategori: {kategori}\n- Deskripsi Ide: {deskripsi}\n\nATURAN:"
            " Jawab SINGKAT, PADAT, dan Maksimal 1-2 kalimat per poin agar"
            " jawaban lengkap dan tidak terpotong!\n\n🎯 **Skor Potensi**:"
            " [Nilai 60-95] - [1 kalimat kesimpulan]\n\n📌 **Rekomendasi"
            " STP**:\n- **Segmenting**: [1 kalimat ringkas]\n- **Targeting**: [1"
            " kalimat ringkas]\n- **Positioning**: [1 kalimat ringkas]\n\n🛍️"
            " **Bauran Pemasaran (4P)**:\n- **Product**: [1 saran ringkas]\n-"
            " **Price**: [1 saran ringkas]\n- **Place**: [1 saran ringkas]\n-"
            " **Promotion**: [1 ide promosi sosmed]\n\n🎓 **Pesan Motivasi**:"
            " [1-2 kalimat inspiratif dan ajakan bergabung dengan Prodi"
            " Manajemen Universitas Karangturi Semarang]"
        )

        try:
            client = Groq(api_key=api_key)

            with st.spinner(
                "🔥 AI sedang meracik strategi bisnis terbaikmu..."
            ):
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

            # Notifikasi Semangat Bertema Api & Roket
            st.toast("🔥 Analisis Selesai! Semangat Berinovasi!", icon="🚀")

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

    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol Reset
    if st.button("🔄 Uji Ide Bisnis Lain / Reset Form", use_container_width=True):
        st.session_state.analyzed = False
        st.session_state.response = ""
        st.session_state.user_data = {}
        st.rerun()

# Footer Copyright
st.markdown(
    """
    <br><hr>
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem;">
        © 2026 <b>Prodi Manajemen Universitas Karangturi Semarang</b> • Student Business Simulator AI
    </div>
""",
    unsafe_allow_html=True,
)
