import os
import time
from groq import Groq
import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Business Pitch Evaluator - Prodi Manajemen",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Custom CSS UI Modern Kualitas Tinggi
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Banner Utama */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }

    /* Card Hasil Evaluasi */
    .eval-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Box Promosi Prodi (CTA) */
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

# 3. Header Hero Banner
st.markdown(
    """
    <div class="hero-container">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🚀</div>
        <div class="hero-title">Student Business Simulator</div>
        <div class="hero-subtitle">Uji & Evaluasi Ide Bisnismu Bersama AI Konsultan dari <b>Prodi Manajemen</b></div>
    </div>
""",
    unsafe_allow_html=True,
)

api_key = st.secrets.get("GROQ_API_KEY")

# 4. Form Input Interaktif untuk Calon Mahasiswa
st.markdown("### 📝 Masukkan Ide Bisnismu")

with st.form("business_form"):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Calon Mahasiswa", placeholder="Misal: Andi")
    with col2:
        sekolah = st.text_input(
            "Asal Sekolah/Instansi", placeholder="Misal: SMAN 1"
        )

    nama_bisnis = st.text_input(
        "Nama Ide Bisnis", placeholder="Misal: Kopi Herbal Nusantara"
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
        "Jelaskan Ide Bisnismu Secara Singkat",
        placeholder=(
            "Apa yang kamu jual? Siapa target pembelinya? Apa keunggulannya dibanding pesaing?"
        ),
        height=100,
    )

    submit_btn = st.form_submit_button(
        "⚡ Analisis Ide Bisnis Sekarang", type="primary", use_container_width=True
    )

# 5. Proses Analisis AI
if submit_btn:
    if not nama_bisnis or not deskripsi:
        st.warning("⚠️ Mohon isi Nama Bisnis dan Penjelasan Ide Bisnis dulu ya!")
    elif not api_key:
        st.error("⚠️ API Key belum terpasang di Streamlit Secrets.")
    else:
        prompt = f"""
        Kamu adalah AI Business Consultant dan Dosen Pakar dari Program Studi Manajemen.
        Tugasmu adalah menganalisis ide bisnis dari calon mahasiswa bernama {nama} ({sekolah}).

        Detail Bisnis:
        - Nama Bisnis: {nama_bisnis}
        - Kategori: {kategori}
        - Deskripsi Ide: {deskripsi}

        Berikan keluaran dalam format yang sangat rapi dan menyemangati:
        1. **Skor Potensi Bisnis** (Berikan nilai angka dari 60 hingga 95 berdasarkan kelogisan ide).
        2. **Analisis Singkat SWOT** (Kekuatan & Tantangan Utama).
        3. **Saran Strategi Pemasaran**: Berikan 2 tips pemasaran praktis.
        4. **Pesan Motivasi Akademis**: Jelaskan mata kuliah di Prodi Manajemen yang bisa membantunya mewujudkan bisnis ini (misal: Manajemen Pemasaran, Kewirausahaan, Studi Kelayakan Bisnis).
        
        Gunakan gaya bahasa profesional, futuristik, ramah, dan memotivasi khas anak muda.
        """

        try:
            client = Groq(api_key=api_key)

            with st.spinner("🧠 AI sedang menganalisis potensi pasarmu..."):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                )
                response = chat_completion.choices[0].message.content

            st.balloons()  # Efek animasi balon perayaan

            # Tampilan Hasil Evaluasi
            st.markdown(
                f"""
                <div class="eval-card">
                    <h3 style="color: #1e3a8a; margin-top:0;">📊 Laporan Evaluasi Bisnis: {nama_bisnis}</h3>
                    <p><b>Calon Innovator:</b> {nama} ({sekolah})</p>
                    <hr>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Menampilkan hasil AI per kata secara streaming
            message_placeholder = st.empty()
            displayed_text = ""
            words = response.split(" ")
            for word in words:
                displayed_text += word + " "
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.01)
            message_placeholder.markdown(response)

            # 6. BANNER PROMOSI & CONVERSION (Call to Action)
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

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

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
