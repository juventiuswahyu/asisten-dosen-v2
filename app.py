import os
from groq import Groq
from PyPDF2 import PdfReader
import streamlit as st

st.set_page_config(
    page_title="Asisten Pengajar AI", page_icon="🎓", layout="centered"
)

st.title("🎓 Asisten Pengajar AI")
st.write(
    "Selamat datang! Silakan tanyakan materi perkuliahan di bawah ini. Jawaban"
    " otomatis diambil dari bahan ajar."
)

# 1. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")


# 2. Fungsi untuk membaca semua PDF yang ada di repository secara otomatis
@st.cache_resource
def load_all_pdfs():
    pdf_text = ""
    # Mencari semua file .pdf di folder utama repository
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
with st.spinner("Memuat bahan ajar..."):
    context_text = load_all_pdfs()

# Riwayat Percakapan
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Form Input Mahasiswa
user_query = st.chat_input("Ketik pertanyaan materi kuliah di sini...")

if user_query:
    if not api_key:
        st.error(
            "⚠️ API Key belum dikonfigurasi di Streamlit Secrets. Silakan tambahkan"
            " GROQ_API_KEY."
        )
    elif not context_text:
        st.warning(
            "⚠️ Belum ada file PDF materi di repository GitHub. Silakan upload"
            " file PDF ke GitHub."
        )
    else:
        # Tampilkan pesan mahasiswa
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user"):
            st.write(user_query)

        # Fitur Pencarian Kata Kunci Sederhana
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
        Kamu adalah Asisten Pengajar AI yang ramah, jelas, dan akurat.
        Jawablah pertanyaan mahasiswa berdasarkan Bahan Ajar berikut:
        
        === BAHAN AJAR ===
        {selected_context}
        ==================
        
        Aturan Jawaban:
        1. Jawab HANYA berdasarkan Bahan Ajar di atas.
        2. Jika jawaban tidak ada di Bahan Ajar, katakan: 'Maaf, materi tersebut tidak ditemukan dalam bahan ajar perkuliahan.'
        3. Gunakan Bahasa Indonesia yang baik dan mudah dipahami.
        
        Pertanyaan Mahasiswa: {user_query}
        """

        try:
            client = Groq(api_key=api_key)

            with st.chat_message("assistant"):
                with st.spinner("Mencari jawaban di bahan ajar..."):
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
