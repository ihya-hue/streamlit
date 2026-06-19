# Import library yang dibutuhkan
import streamlit as st          # framework web app
import google.generativeai as genai         # SDK Gemini dari Google
import json                      # Untuk menyimpan/memuat riwayat chat
import base64                    # Untuk encoding/decoding gambar ke/dari JSON
# import requests                  # Untuk mengambil data dari API cuaca
import os                        # Untuk membaca variabel lingkungan
from dotenv import load_dotenv   # Untuk memuat variabel lingkungan dari .env

# Muat variabel lingkungan dari file .env
load_dotenv()

# Function to prune chat history
def prune_chat_history(messages_list, max_len):
    """Prunes the chat history list to the specified maximum length."""
    if messages_list and len(messages_list) > max_len:
        # Keep only the last 'max_len' messages
        return messages_list[-max_len:]
    return messages_list

# Set page config for browser tab title
st.set_page_config(page_title="Kembara Traveler | Tanya • Rencana • Kembara", page_icon="✨", layout="wide")

# Global Session State Initializations for Chatbot Settings (for robustness)
# Ensure these are initialized once per session, before any widgets or logic use them
# Ambil GOOGLE_API_KEY dari variabel lingkungan (dari .env atau Colab Secrets)
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY", "")

if "conversation_style" not in st.session_state:
    st.session_state.conversation_style = "Santai"
if "_last_conversation_style" not in st.session_state:
    st.session_state._last_conversation_style = st.session_state.conversation_style # Match initial state

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "_last_temperature" not in st.session_state:
    st.session_state._last_temperature = st.session_state.temperature # Match initial state

if "max_history_length" not in st.session_state:
    st.session_state.max_history_length = 20

if "travel_preferences" not in st.session_state:
    st.session_state.travel_preferences = []
if "_last_travel_preferences" not in st.session_state:
    st.session_state._last_travel_preferences = st.session_state.travel_preferences # Match initial state

if "preferred_destination" not in st.session_state:
    st.session_state.preferred_destination = ""
if "_last_preferred_destination" not in st.session_state:
    st.session_state._last_preferred_destination = st.session_state.preferred_destination # Match initial state

# Initialize chat session in st.session_state if not already present
# This will store the chat history and the GenerativeModel instance
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None # Will be initialized when API key is valid

if "genai_client" not in st.session_state:
    st.session_state.genai_client = None

if "_last_api_key" not in st.session_state:
    st.session_state._last_api_key = None


# ── Global App Title and Navigation ──────────────────────────────────────────
st.title("Kembara Traveler")
st.caption("Aplikasi perjalanan cerdas Anda: Tanya, Rencana, Kembara")

# --- Main Page Navigation (using st.tabs for a cleaner look) ---
# Define the tabs
home_tab, itinerary_tab, chatbot_tab, tools_tab = st.tabs(
    ["🏠 Home", "🗺️ Itinerary", "💬 Chatbot", "💼 Tools"]
)

# ── Page Content Rendering ───────────────────────────────────────────────────
with home_tab:
    st.header("🏠 Selamat Datang di Kembara Traveler!")
    st.markdown("Dashboard perjalanan Anda yang personal. Di sini Anda bisa melihat ringkasan dan rekomendasi perjalanan.")
    st.subheader("Dashboard Perjalanan Anda")
    st.write("*(Konten dashboard akan muncul di sini: ringkasan perjalanan, statistik, dll.)*")

with itinerary_tab:
    st.header("🗺️ Rencana Perjalanan Anda")
    st.markdown("Kelola linemasa perjalanan, lihat peta rute, dan pantau anggaran Anda.")
    st.subheader("Linemasa Perjalanan")
    st.write("*(Linemasa detail perjalanan Anda per hari/jam akan muncul di sini.)*")
    st.subheader("Peta Rute")
    st.write("*(Peta interaktif dengan rute perjalanan Anda akan muncul di sini.)*")
    st.subheader("Manajer Anggaran")
    st.write("*(Alat untuk melacak pengeluaran perjalanan Anda akan muncul di sini.)*")

with chatbot_tab:
    st.header("💬 Interaksi dengan Kembara AI") # Use header for page title
    # st.markdown("Jendela chatbot interaktif tempat Anda dapat bertanya dan merencanakan perjalanan.") # Use markdown for descriptive text

    # --- Chatbot-specific settings in sidebar ---
    with st.sidebar:
        # st.markdown("---") # Separator
        st.subheader("Pengaturan Chatbot")

        # Selectbox for conversation style
        st.session_state.conversation_style = st.selectbox(
            "Gaya Percakapan",
            ("Santai", "Formal"),
            index=0 if st.session_state.conversation_style == "Santai" else 1, # Use index to pre-select
            help="Pilih gaya bahasa yang diinginkan untuk chatbot.")

        # Add temperature slider
        st.session_state.temperature = st.slider(
            "Suhu (Temperature) Model",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature, # Now this will always be initialized globally
            step=0.05,
            help="Kontrol tingkat kreativitas respons AI. Nilai lebih tinggi (mendekati 1.0) menghasilkan respons yang lebih bervariasi dan kreatif; nilai lebih rendah (mendekati 0.0) menghasilkan respons yang lebih fokus dan konservatif.")

        uploaded_file = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png", "gif"])

        # Number input for max history length
        st.session_state.max_history_length = st.number_input(
            "Batasi Riwayat Chat (Pesan)",
            min_value=5,
            max_value=50,
            value=st.session_state.max_history_length, # Use the globally initialized value
            step=5,
            help="Jumlah maksimum pesan (user dan assistant) yang akan disimpan dan ditampilkan di riwayat chat.")

        st.subheader("Pengaturan Preferensi Perjalanan (Profil)")
        # Multiselect for travel preferences
        st.session_state.travel_preferences = st.multiselect(
            "Pilih Preferensi Perjalanan Anda",
            ['Petualangan', 'Bersantai', 'Budaya', 'Kuliner', 'Sejarah', 'Alam', 'Belanja', 'Edukasi'],
            default=st.session_state.travel_preferences, # Use the globally initialized value
            help="Pilih jenis perjalanan yang Anda minati. Ini akan membantu Kembara memberikan rekomendasi yang lebih baik.")
        # Text input for preferred destination
        st.session_state.preferred_destination = st.text_input(
            "Destinasi Pilihan (Opsional)",
            value=st.session_state.preferred_destination, # Use the globally initialized value
            help="Jika ada destinasi khusus yang Anda pertimbangkan, sebutkan di sini.")

        reset_button = st.button("Reset Percakapan", help="Hapus semua pesan dan mulai dari awal", key="chatbot_reset_button") # Unique key

        # Download chat history features (remain within chatbot settings as they are chatbot specific)
        if st.session_state.get("messages"):
            chat_history_text = ""
            # Generate chat history text from messages that have content
            for msg in st.session_state.messages:
                if msg.get("content"): # Only include messages with content
                    chat_history_text += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

            if chat_history_text: # Only show download button if there's actual chat content
                st.download_button(
                    label="Download Riwayat Chat (Text)",
                    data=chat_history_text.encode('utf-8'),
                    file_name="kembara_chat_history.txt",
                    mime="text/plain")

        if st.session_state.get("messages"):
            serializable_messages = []
            for msg in st.session_state.messages:
                if "image" in msg and msg["image"] is not None:
                    # Base64 encode image bytes for JSON serialization
                    serializable_messages.append({
                        "role": msg["role"],
                        "content": msg.get("content", ""),
                        "image_base64": base64.b64encode(msg["image"]).decode('utf-8')
                    })
                else:
                    serializable_messages.append(msg)
            json_chat_history = json.dumps(serializable_messages, indent=2)

            if serializable_messages: # Only show download button if there's actual chat content
                st.download_button(
                    label="Download Riwayat Chat (JSON)",
                    data=json_chat_history.encode('utf-8'),
                    file_name="kembara_chat_history.json",
                    mime="application/json")

    # --- Main Chatbot Logic ---
    # Re-initialize or configure the generative model if API key or settings change
    current_api_key = st.session_state.google_api_key
    current_conversation_style = st.session_state.conversation_style
    current_temperature = st.session_state.temperature

    # Check if API key or any relevant settings have changed
    if (
        st.session_state.genai_client is None or
        current_api_key != st.session_state._last_api_key or
        current_conversation_style != st.session_state._last_conversation_style or
        current_temperature != st.session_state._last_temperature
    ):

        if current_api_key:
            try:
                genai.configure(api_key=current_api_key)
                # Model configuration based on conversation style
                if current_conversation_style == "Santai":
                    model_name = "gemini-1.5-flash-latest" # A more creative model
                else:
                    model_name = "gemini-1.5-pro-latest"   # A more factual/formal model

                st.session_state.genai_client = genai.GenerativeModel(model_name=model_name,
                                                                    generation_config={
                                                                        "temperature": current_temperature
                                                                    })
                st.session_state.chat = st.session_state.genai_client.start_chat(history=st.session_state.messages)
                st.session_state._last_api_key = current_api_key
                st.session_state._last_conversation_style = current_conversation_style
                st.session_state._last_temperature = current_temperature
                st.success("Gemini API dikonfigurasi dan siap!")
            except Exception as e:
                st.session_state.genai_client = None
                st.session_state.chat = None
                st.error(f"Gagal mengkonfigurasi Gemini API. Cek API key Anda: {e}")
                st.stop()
        else:
            st.warning("Harap masukkan Google AI API Key Anda.")
            st.session_state.genai_client = None
            st.session_state.chat = None
            st.stop()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message and message["image"] is not None:
                st.image(message["image"], caption="Gambar Anda", use_column_width=True)

    # React to user input
    if prompt := st.chat_input("Ketik pesanmu..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare content for Gemini API
        contents = [prompt]
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            contents.append(
                {
                    'mime_type': uploaded_file.type,
                    'data': image_data
                }
            )
            st.session_state.messages[-1]["image"] = image_data # Store image in session state

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Generate response from Gemini
            try:
                if st.session_state.chat:
                    stream = st.session_state.chat.send_message(contents, stream=True)
                    for chunk in stream:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error("Chat session belum diinisialisasi. Cek API key Anda.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil Gemini API: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Maaf, terjadi kesalahan: {e}"})

    # Prune chat history after adding new messages, but before the next run
    st.session_state.messages = prune_chat_history(st.session_state.messages, st.session_state.max_history_length)

    # Clear conversation if reset button is clicked
    if reset_button:
        st.session_state.messages = []
        st.session_state.chat = None # Re-initialize chat session
        st.rerun()

with tools_tab:
    st.header("💼 Tools")
    st.markdown("Di sini Anda dapat menemukan berbagai alat bantu perjalanan yang berguna.")
    st.subheader("Konverter Mata Uang")
    st.write("*(Alat konversi mata uang akan muncul di sini.)*")
    st.subheader("Daftar Periksa Perjalanan")
    st.write("*(Daftar periksa barang bawaan dan persiapan perjalanan akan muncul di sini.)*")


# --- Final Cleanup / Session State Management ---
# Ensure button moves to the bottom of the sidebar. This is usually handled by order of elements.
# If you need a persistent element at the very bottom, it's often placed after other sidebar elements.
with st.sidebar:
    if st.button("Bersihkan Cache Sesi", help="Menghapus semua data sesi Streamlit."):
        st.session_state.clear()
        st.success("Cache sesi telah dibersihkan!")
        st.rerun() # Rerun to reflect changes
