import base64
import os
from groq import Groq
from PyPDF2 import PdfReader
import streamlit as st

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Asisten Dosen AI",
    page_icon="foto_dosen.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Fungsi untuk membaca foto .png lokal dan mengonversinya ke Base64
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""


img_b64 = get_image_base64("foto_dosen.png")
img_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""

# 2. Custom CSS Tampilan Modern
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .header-subtitle {
        font-size: 0.95rem;
        opacity: 0.9;
    }
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

# 3. Banner Utama
st.markdown(
    f"""
    <div class="header-container">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
            <img src="{img_src}" style="width: 120px; height: 120px; border-radius: 50%; border: 3.5px solid white; object-fit: cover; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
        </div>
        <div class="header-title">🎓 Asisten Akademik AI</div>
        <div class="header-subtitle">Tanyakan materi perkuliahan dan konsep Pemasaran pada Bahan Ajar.</div>
        <div class="status-badge">⚡ Powered by Groq AI • Aktif 24/7</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 4. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")


# 5. Fungsi Membaca PDF
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


with st.spinner("🔍 Memuat bahan ajar perkuliahan..."):
    context_text = load_all_pdfs()

# 6. Riwayat Percakapan
if "messages" not in st.session_state:
    st.session_state.messages = []

# Avatar bot menggunakan foto_dosen.png
avatar_bot = "foto_dosen.png" if os.path.exists("foto_dosen.png") else "🤖"

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown("**Mahasiswa**")
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar=avatar_bot):
            st.markdown("**Asisten Pak Juven**")
            st.write(msg["content"])

# 7. Form Input Pertanyaan Mahasiswa
user_query = st.chat_input("Tanyakan sesuatu tentang materi perkuliahan...")

if user_query:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY belum dikonfigurasi di Streamlit Secrets.")
    elif not context_text:
        st.warning("⚠️ Belum ada file PDF materi di repository.")
    else:
        # Tampilkan Pesan Mahasiswa
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown("**Mahasiswa**")
            st.write(user_query)

        # Pencarian Kata Kunci Relevan
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
        Kamu adalah Asisten Pengajar AI dari Pak Juven yang ramah, profesional, dan akademis.
        Jawablah pertanyaan mahasiswa berdasarkan Bahan Ajar berikut:
        
        === BAHAN AJAR ===
        {selected_context}
        ==================
        
        Aturan Jawaban:
        1. Jawab HANYA berdasarkan Bahan Ajar di atas.
        2. Jika tidak ada di bahan ajar, katakan dengan sopan: 'Maaf, materi tersebut tidak ditemukan dalam bahan ajar perkuliahan.'
        3. Gunakan Bahasa Indonesia yang baik dan poin-poin jika diperlukan.
        
        Pertanyaan Mahasiswa: {user_query}
        """

        try:
            client = Groq(api_key=api_key)

            # Tampilkan pesan Asisten AI dengan Label "Asisten Pak Juven"
            with st.chat_message("assistant", avatar=avatar_bot):
                st.markdown("**Asisten Pak Juven**")
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
            st.error(f"Terjadi kesalahan: {e}")
