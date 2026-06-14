import subprocess
import time

def run_streamlit(filename, port=8501):
    # Kill SEMUA proses streamlit, bukan hanya yang kita spawn
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)

    # Force-free port kalau masih ada yang nempel
    subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)

    # Tutup semua tunnel ngrok
    ngrok.kill()

    # Tunggu port benar-benar bebas
    time.sleep(3)

    proc = subprocess.Popen(
        [
            "streamlit", "run", filename,
            "--server.headless=true",
            "--server.port", str(port),
            "--server.enableCORS=false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(3)

    public_url = ngrok.connect(port)
    print(f"Streamlit berjalan: {public_url}")

    return proc
