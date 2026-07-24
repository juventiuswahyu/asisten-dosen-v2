import base64
import os
import time
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

# 2. Custom CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Banner Header */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
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

    /* Footer Hak Cipta */
    .custom-footer {
        text-align: center;
        color: #777777;
        font-size: 0.82rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }

    /* Efek Chat Bubble */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    /* Chat Asisten (Kiri/Putih) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    /* Chat Mahasiswa (Kanan/Aksen Biru Muda) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f0f4f9;
        border: 1px solid #d0dbe7;
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

# Avatar bot
avatar_bot = "foto_dosen.png" if os.path.exists("foto_dosen.png") else "🤖"
label_bot = '<span style="color: #1e3c72; font-weight: bold; font-size: 1.05rem;">Asisten Pak Juven</span>'
label_user = '<span style="color: #555555; font-weight: bold;">Mahasiswa</span>'

# --- HEADLINE CONTROLS & TOMBOL RESET ---
col_title, col_reset = st.columns([3, 1])
with col_title:
    st.markdown("**💡 Contoh Pertanyaan Cepat:**")
with col_reset:
    # FITUR RESET CHAT
    if st.button("🔄 Reset Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- FITUR: PILIHAN PERTANYAAN CEPAT ---
col1, col2, col3 = st.columns(3)
prompt_to_submit = None

if col1.button("📌 Apa itu Pemasaran?", use_container_width=True):
    prompt_to_submit = "Apa definisi dan konsep utama Pemasaran menurut Bahan Ajar?"
if col2.button("💡 Bauran Pemasaran (4P)", use_container_width=True):
    prompt_to_submit = "Jelaskan tentang Bauran Pemasaran (Marketing Mix) 4P!"
if col3.button("🎯 Perencanaan Strategis", use_container_width=True):
    prompt_to_submit = "Bagaimana proses perencanaan strategis pemasaran?"

st.write("---")

# Tampilkan Percakapan Sebelumnya
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(label_user, unsafe_allow_html=True)
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar=avatar_bot):
            st.markdown(label_bot, unsafe_allow_html=True)
            st.write(msg["content"])

# Form Input Manual
user_input = st.chat_input("Tanyakan sesuatu tentang materi perkuliahan Pemasaran...")

# Prioritaskan input dari tombol cepat jika ada
if prompt_to_submit:
    user_query = prompt_to_submit
elif user_input:
    user_query = user_input
else:
    user_query = None

# 7. Proses Pertanyaan & Jawaban
if user_query:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY belum dikonfigurasi di Streamlit Secrets.")
    elif not context_text:
        st.warning("⚠️ Belum ada file PDF materi di repository.")
    else:
        # Tampilkan Pesan Mahasiswa
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(label_user, unsafe_allow_html=True)
            st.write(user_query)

        # Pencarian Kata Kunci
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

            with st.chat_message("assistant", avatar=avatar_bot):
                st.markdown(label_bot, unsafe_allow_html=True)

                # Dapatkan respons dari Groq AI
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                )
                full_response = chat_completion.choices[0].message.content

                # EFEK KETIK OTOMATIS (STREAMING)
                message_placeholder = st.empty()
                displayed_text = ""

                words_list = full_response.split(" ")
                for i, word in enumerate(words_list):
                    displayed_text += word + " "
                    message_placeholder.markdown(displayed_text + "▌")
                    time.sleep(0.02)

                message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# FOOTER HAK CIPTA
st.markdown(
    """
    <div class="custom-footer">
        © 2026 <b>Asisten Akademik Pak Juven</b> • Hak Cipta Dilindungi Undang-Undang<br>
        <i>Khusus dipergunakan untuk Lingkungan Perkuliahan Manajemen Pemasaran.</i>
    </div>
""",
    unsafe_allow_html=True,
)
