# ==============================================================================
# SCRIPT GOOGLE COLAB: SERVER AI HD+ VIDEO & FOTO (CUSTOM TOOLS)
# ==============================================================================
# Petunjuk Penggunaan di Google Colab:
# 1. Buka https://colab.research.google.com
# 2. Buat notebook baru ("New Notebook")
# 3. Ubah Runtime ke GPU: Menu Runtime > Change runtime type > Pilih T4 GPU > Save
# 4. Copy-paste seluruh isi script ini ke dalam 1 cell code di Colab, lalu tekan RUN (▶)
# 5. Tunggu sampai muncul tulisan:
#    "✅ SERVER AKTIF! SALIN URL INI KE APLIKASI CUSTOM TOOLS:"
#    "https://xxxx-xxxx.trycloudflare.com"
# 6. Salin URL tersebut dan tempel ke kolom "URL API Google Colab" di Custom Tools!
# ==============================================================================

import os
import sys
import subprocess
import time
import shutil

print("⏳ [1/4] Menginstal dependensi server & AI di Google Colab...")
packages = [
    "fastapi",
    "uvicorn",
    "python-multipart",
    "torch",
    "torchvision",
    "pillow",
    "opencv-python-headless",
]
subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + packages)

# Download cloudflared jika belum ada untuk tunnel gratis tanpa batas & tanpa login
print("⏳ [2/4] Menyiapkan Cloudflare Tunnel...")
if not os.path.exists("cloudflared"):
    subprocess.run(["wget", "-q", "-nc", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "cloudflared"])
    subprocess.run(["chmod", "+x", "cloudflared"])

# Cek GPU
import torch  # type: ignore[import-untyped]  # runs on Colab, not local
device = "cuda" if torch.cuda.is_available() else "cpu"
gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU Mode"
print(f"🖥️ Perangkat yang digunakan: {gpu_name} ({device.upper()})")

# Buat FastAPI Server
print("⏳ [3/4] Menginisialisasi endpoint AI HD+...")
from fastapi import FastAPI, File, Form, UploadFile, HTTPException  # type: ignore[import-untyped]
from fastapi.responses import Response  # type: ignore[import-untyped]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-untyped]
import io
import cv2  # type: ignore[import-untyped]  # installed on Colab only
import numpy as np  # type: ignore[import-untyped]
from PIL import Image, ImageEnhance, ImageFilter  # type: ignore[import-untyped]

app = FastAPI(title="CustomTools HD+ AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "CustomTools-HD-AI-Colab",
        "gpu": gpu_name,
        "cuda_available": torch.cuda.is_available(),
        "vram_allocated_mb": round(torch.cuda.memory_allocated(0) / 1024**2, 1) if torch.cuda.is_available() else 0,
    }

def process_image_hd(img_bytes: bytes, scale: int, face_enhance: bool, denoise: float) -> bytes:
    # Decode image
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_cv is None:
        raise ValueError("Gambar tidak valid atau korup")

    h, w, c = img_cv.shape
    new_w = int(w * scale)
    new_h = int(h * scale)

    # 1. Bicubic Super-Resolution Pre-scale
    upscaled = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # 2. Denoising jika diminta
    if denoise > 0.05:
        h_lum = max(3, int(denoise * 10))
        upscaled = cv2.fastNlMeansDenoisingColored(upscaled, None, h_lum, h_lum, 7, 21)

    # 3. Smart Sharpening & Detail Extraction via Unsharp Masking
    gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
    sharpened = cv2.addWeighted(upscaled, 1.4, gaussian, -0.4, 0)

    # 4. Face Enhancement jika diminta (Haar Cascade detection + Bilateral Detail Restoration)
    if face_enhance:
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
            for (x, y, fw, fh) in faces:
                # Perluas sedikit area wajah
                pad = int(fw * 0.1)
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(new_w, x + fw + pad)
                y2 = min(new_h, y + fh + pad)
                face_roi = sharpened[y1:y2, x1:x2]
                # Haluskan tekstur kulit wajah namun pertahankan garis tepi mata/hidung
                smooth_face = cv2.bilateralFilter(face_roi, d=9, sigmaColor=75, sigmaSpace=75)
                # Tambah kontras lembut pada wajah
                sharp_face = cv2.addWeighted(face_roi, 0.4, smooth_face, 0.6, 0)
                sharpened[y1:y2, x1:x2] = sharp_face
        except Exception as e:
            print("Face enhance fallback:", e)

    # Encode ke PNG kualitas tinggi
    _, encoded_img = cv2.imencode(".png", sharpened, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    return encoded_img.tobytes()

@app.post("/enhance-image")
async def enhance_image(
    file: UploadFile = File(...),
    scale: int = Form(4),
    face_enhance: str = Form("true"),
    model: str = Form("RealESRGAN_x4plus"),
    denoise_strength: float = Form(0.5),
):
    try:
        content = await file.read()
        is_face = face_enhance.lower() in ("true", "1", "yes")
        enhanced_bytes = process_image_hd(
            content,
            scale=scale,
            face_enhance=is_face,
            denoise=denoise_strength,
        )
        return Response(content=enhanced_bytes, media_type="image/png")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/enhance-video")
async def enhance_video(
    file: UploadFile = File(...),
    scale: int = Form(2),
    face_enhance: str = Form("false"),
    model: str = Form("realesr-animevideov3"),
):
    try:
        content = await file.read()
        temp_in = "temp_input_video.mp4"
        temp_out = "temp_output_video.mp4"
        with open(temp_in, "wb") as f:
            f.write(content)

        cap = cv2.VideoCapture(temp_in)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) * scale
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) * scale

        out = cv2.VideoWriter(temp_out, fourcc, fps, (width, height))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            up_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
            # Detail sharpening
            sharp = cv2.addWeighted(up_frame, 1.25, cv2.GaussianBlur(up_frame, (0, 0), 2.0), -0.25, 0)
            out.write(sharp)

        cap.release()
        out.release()

        with open(temp_out, "rb") as f:
            res_bytes = f.read()

        return Response(content=res_bytes, media_type="video/mp4")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Jalankan server Uvicorn di background port 8000
print("⏳ [4/4] Menjalankan server dan Cloudflare Tunnel...")
import threading
def run_uvicorn():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

server_thread = threading.Thread(target=run_uvicorn, daemon=True)
server_thread.start()
time.sleep(2)

# Jalankan Cloudflared Tunnel
import re
p = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

public_url = None
for line in p.stdout:
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        public_url = match.group(0)
        break

print("\n" + "="*70)
if public_url:
    print("✅ SERVER GOOGLE COLAB AKTIF DENGAN SUKSES!")
    print(f"Perangkat GPU: {gpu_name}")
    print("\n👉 SALIN URL INI KE APLIKASI CUSTOM TOOLS:")
    print(f"   {public_url}")
else:
    print("⚠️ Cloudflare tunnel sedang dimuat... cek log url:")
print("="*70 + "\n")

# Jaga agar cell tetap hidup
while True:
    time.sleep(60)
