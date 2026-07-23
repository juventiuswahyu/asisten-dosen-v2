from groq import Groq
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="Asisten Pengajar AI", page_icon="🎓", layout="centered"
)

st.title("🎓 Asisten Pengajar AI")
st.write(
    "Selamat datang! Silakan tanyakan materi perkuliahan atau soal di bawah"
    " ini."
)

# 1. Mengambil API Key secara otomatis dari Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")

# 2. Sidebar khusus Dosen untuk upload PDF
with st.sidebar:
    st.header("⚙️ Area Dosen")
    uploaded_files = st.file_uploader(
        "Unggah Materi PDF Kuliah di sini:",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file PDF berhasil dimuat!")

# Ekstraksi Teks dari PDF
context_text = ""
if uploaded_files:
    for file in uploaded_files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                context_text += text

    # Membatasi jumlah teks agar tidak melebih batas token limit Groq
    if len(context_text) > 35000:
        context_text = context_text[:35000]

# Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Kolom Pertanyaan Mahasiswa
user_query = st.chat_input("Ketik pertanyaan kamu di sini...")

if user_query:
    if not api_key:
        st.error(
            "⚠️ Sistem belum siap (API Key belum diatur oleh Dosen di Secrets)."
        )
    elif not context_text:
        st.warning(
            "⚠️ Belum ada materi PDF yang diunggah oleh Dosen. Silakan hubungi"
            " Dosen kamu."
        )
    else:
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user"):
            st.write(user_query)

        prompt = f"""
        Kamu adalah Asisten Pengajar yang ramah, sopan, dan akurat.
        Jawablah pertanyaan mahasiswa HANYA berdasarkan bahan ajar berikut:
        
        {context_text}
        
        Aturan:
        1. Jika jawaban TIDAK ADA di dalam bahan ajar di atas, katakan dengan sopan: 'Maaf, materi tersebut tidak ditemukan dalam bahan ajar yang diunggah oleh Dosen.'
        2. Berikan penjelasan yang rinci dan mudah dipahami dalam Bahasa Indonesia.
        
        Pertanyaan Mahasiswa: {user_query}
        """

        try:
            client = Groq(api_key=api_key)

            with st.chat_message("assistant"):
                with st.spinner("Mencari jawaban dari bahan ajar..."):
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant",  # Model hemat token & cepat
                    )
                    answer = chat_completion.choices[0].message.content
                    st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan pada sistem: {e}")
