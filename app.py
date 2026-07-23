from openai import OpenAI
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(page_title="Asisten Pengajar AI", page_icon="🎓")
st.title("🎓 Asisten Pengajar AI")
st.write(
    "Silakan tanyakan soal atau materi perkuliahan di bawah ini. Jawaban akan"
    " langsung bersumber dari materi PDF."
)

with st.sidebar:
    st.header("⚙️ Panel Dosen")
    api_key = st.text_input("Masukkan Gemini API Key Anda:", type="password")
    uploaded_files = st.file_uploader(
        "Unggah PDF Materi Kuliah:", type=["pdf"], accept_multiple_files=True
    )

context_text = ""
if uploaded_files:
    for file in uploaded_files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                context_text += text

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_query = st.chat_input("Ketik pertanyaan atau soal di sini...")

if user_query:
    if not api_key:
        st.error(
            "⚠️ Masukkan Gemini API Key di menu sebelah kiri terlebih dahulu!"
        )
    elif not context_text:
        st.warning("⚠️ Dosen belum mengunggah berkas PDF materi kuliah.")
    else:
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )
        with st.chat_message("user"):
            st.write(user_query)

        prompt = f"""
        Kamu adalah Asisten Pengajar yang ramah dan akurat.
        Jawablah pertanyaan mahasiswa HANYA berdasarkan bahan ajar berikut:
        
        {context_text}
        
        Aturan:
        1. Jika jawaban TIDAK ADA di dalam bahan ajar di atas, katakan dengan sopan: 'Maaf, materi tersebut tidak ditemukan dalam bahan ajar yang diunggah oleh Dosen.'
        2. Berikan penjelasan yang rinci dan mudah dipahami.
        
        Pertanyaan: {user_query}
        """

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            )

            with st.chat_message("assistant"):
                with st.spinner("Mencari jawaban dari materi..."):
                    response = client.chat.completions.create(
                        model="gemini-2.0-flash",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
