import os
from groq import Groq
from PyPDF2 import PdfReader
import streamlit as st

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Asisten Dosen AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Custom CSS untuk mempercantik Tampilan (UI)
st.markdown(
    """
    <style>
    /* Sembunyikan Header dan Footer Bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Styling Banner Header */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 300;
    }

    /* Styling Badge Status */
    .status-badge {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Tampilan Header Utama
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">🎓 Asisten Akademik AI</div>
        <div class="header-subtitle">Tanyakan hal terkait materi perkuliahan, tugas, atau konsep bahan ajar.</div>
        <div class="status-badge">⚡ Powered by Groq AI • Aktif 24/7</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 4. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")


# 5. Fungsi untuk membaca semua PDF di repository
@st.cache_resource
def load_all_pdfs():
    pdf_text = ""
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
            except Exception as e:
                print(f"Gagal membaca file {file}: {e}")
    return pdf_text


# Load materi otomatis di awal
with st.spinner("🔍 Memuat bahan ajar perkuliahan..."):
    context_text = load_all_pdfs()

# 6. Riwayat Percakapan Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan pesan yang tersimpan di memori
for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 7. Form Input Pertanyaan
user_query = st.chat_input("Tanyakan sesuatu tentang materi perkuliahan...")

if user_query:
    if not api_key:
        st.error(
            "⚠️ API Key belum terkonfigurasi. Pastikan GROQ_API_KEY ada di"
            " Secrets."
        )
    elif not context_text:
        st.warning("⚠️ Belum ada file PDF materi perkuliahan di server.")
    else:
        # Tampilkan pertanyaan user
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.write(user_query)

        # Fitur Pencarian Kata Kunci Relevan
        words = user_query.lower().split()
        paragraphs = context_text.split("\n\n")
        relevant_paragraphs = []

        for p in paragraphs:
            if any(word in p.lower() for word in words if len(word) > 3):
                relevant_paragraphs.append(p)

        if relevant_paragraphs:
            selected_context = "\n".join(relevant_paragraphs[:10])
        else:
            selected_context = context_text[:15000]

        if len(selected_context) > 20000:
            selected_context = selected_context[:20000]

        prompt = f"""
        Kamu adalah Asisten Pengajar AI yang profesional, ramah, dan akademis.
        Jawablah pertanyaan mahasiswa berdasarkan Bahan Ajar berikut:
        
        === BAHAN AJAR ===
        {selected_context}
        ==================
        
        Aturan Jawaban:
        1. Jawab HANYA berdasarkan Bahan Ajar di atas.
        2. Jika jawaban tidak ada di Bahan Ajar, katakan dengan sopan: 'Maaf, materi tersebut tidak ditemukan dalam bahan ajar perkuliahan.'
        3. Gunakan Bahasa Indonesia yang rapi, profesional, dan mudah dipahami.
        4. Gunakan poin-poin (bullet points) jika penjelasan membutuhkan daftar agar lebih mudah dibaca.
        
        Pertanyaan Mahasiswa: {user_query}
        """

        try:
            client = Groq(api_key=api_key)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Sedang menganalisis bahan ajar..."):
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant",
                    )
                    answer = chat_completion.choices[0].message.content
                    st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan pada sistem: {e}")
