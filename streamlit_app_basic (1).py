import streamlit as st
import pandas as pd
import numpy as np
import time

# ── Judul & Intro ────────────────────────────────────────────────────────────
st.title("Streamlit Basic Tutorial")
st.write("""
## Selamat datang di Streamlit!

Ini adalah demo komponen-komponen dasar yang tersedia di Streamlit.
Setiap section di bawah menunjukkan cara kerja satu komponen.
""")

# ── 1. Text Input ────────────────────────────────────────────────────────────
st.header("1. Text Input")
st.write("""`st.text_input()` membuat kotak teks. Nilai yang diketik user disimpan di variabel.""")
user_input = st.text_input("Masukkan namamu", "Ketik di sini...")
st.write(f"Halo, {user_input}!")

# ── 2. Button ────────────────────────────────────────────────────────────────
st.header("2. Button")
st.write("""`st.button()` mengembalikan `True` saat diklik (lalu kembali ke `False`).""")
if st.button("Klik aku!"):
    st.write("Tombol diklik!")

# ── 3. Checkbox ──────────────────────────────────────────────────────────────
st.header("3. Checkbox")
st.write("""`st.checkbox()` adalah toggle yang mengembalikan `True` saat dicentang.""")
show_content = st.checkbox("Tampilkan pesan rahasia")
if show_content:
    st.write("Kamu menemukan pesan rahasianya!")

# ── 4. Selectbox ─────────────────────────────────────────────────────────────
st.header("4. Selectbox")
st.write("""`st.selectbox()` membuat dropdown untuk memilih satu opsi.""")
option = st.selectbox("Pilih warna favoritmu", ("Merah", "Biru", "Hijau", "Kuning"))
st.write(f"Kamu memilih: {option}")

# ── 5. Slider ────────────────────────────────────────────────────────────────
st.header("5. Slider")
st.write("""`st.slider()` membuat slider untuk memilih nilai angka secara interaktif.""")
age = st.slider("Berapa umurmu?", 0, 100, 25)
st.write(f"Umurmu adalah {age} tahun")

# ── 6. Progress Bar ──────────────────────────────────────────────────────────
st.header("6. Progress Bar")
st.write("""`st.progress()` menampilkan bar progress yang bisa diupdate.""")
progress_bar = st.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress_bar.progress(i + 1)
st.write("Selesai!")

# ── 7. Sidebar ───────────────────────────────────────────────────────────────
st.header("7. Sidebar")
st.write("""`st.sidebar` membuat panel samping yang bisa disembunyikan.""")
with st.sidebar:
    st.header("Panel Samping")
    st.write("Widget di sini tidak mengganggu konten utama.")
    if st.button("Tombol di Sidebar"):
        st.write("Tombol sidebar diklik!")

# ── 8. Columns ───────────────────────────────────────────────────────────────
st.header("8. Columns")
st.write("""`st.columns()` membagi halaman menjadi beberapa kolom.""")
col1, col2 = st.columns(2)
with col1:
    st.write("Ini kolom kiri")
    st.button("Tombol di kolom kiri")
with col2:
    st.write("Ini kolom kanan")
    st.button("Tombol di kolom kanan")

# ── 9. Status Messages ───────────────────────────────────────────────────────
st.header("9. Status Messages")
st.success("Ini pesan sukses!")
st.info("Ini pesan informasi")
st.warning("Ini pesan peringatan")
st.error("Ini pesan error")

# ── 10. Charts ───────────────────────────────────────────────────────────────
st.header("10. Charts")

st.subheader("Line Chart")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["Metrik A", "Metrik B", "Metrik C"]
)
st.line_chart(chart_data)

st.subheader("Bar Chart")
bar_data = pd.DataFrame(
    {"Apel": [10, 25, 18, 30], "Mangga": [15, 12, 22, 8]},
    index=["Jan", "Feb", "Mar", "Apr"]
)
st.bar_chart(bar_data)

# ── 11. Dataframe ────────────────────────────────────────────────────────────
st.header("11. Dataframe & Tabel")
data = {
    "Nama":  ["Alice", "Bob", "Charlie", "Diana"],
    "Skor":  [88, 72, 95, 80],
    "Level": ["A", "B", "A+", "A"],
}
df = pd.DataFrame(data)
st.write("Tabel interaktif (`st.dataframe`):")
st.dataframe(df)
st.write("Statistik deskriptif:")
st.write(df.describe())
