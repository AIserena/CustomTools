"""Core operations for HD+ Video & Photo enhancement integrated with Google Colab API."""

import io
import time
from typing import Any, Dict, Tuple
import requests
from PIL import Image


def check_colab_health(api_url: str, timeout: int = 6) -> Dict[str, Any]:
    """Test connection to the Google Colab enhancement server.
    
    Returns a dict with 'connected', 'status_code', 'details', and 'message'.
    """
    if not api_url or not str(api_url).strip():
        return {
            "connected": False,
            "status_code": 0,
            "message": "URL API Google Colab belum diisi.",
            "details": {},
        }

    base_url = str(api_url).strip().rstrip("/")
    if not (base_url.startswith("http://") or base_url.startswith("https://")):
        base_url = "https://" + base_url

    headers = {
        "User-Agent": "CustomTools-Enhancer-Client/1.0",
        "ngrok-skip-browser-warning": "true",  # Bypass ngrok free splash page
        "Bypass-Tunnel-Reminder": "true",       # Localtunnel bypass
    }

    # First try /health, then fallback to /
    endpoints = [f"{base_url}/health", f"{base_url}/"]
    last_err = None

    for url in endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {"response": resp.text[:200]}
                return {
                    "connected": True,
                    "status_code": 200,
                    "message": "Terhubung dengan sukses ke Google Colab!",
                    "details": data,
                    "base_url": base_url,
                }
        except Exception as e:
            last_err = e

    return {
        "connected": False,
        "status_code": 0,
        "message": f"Tidak dapat terhubung ke Colab: {last_err}",
        "details": {},
        "base_url": base_url,
    }


def enhance_image_colab(
    api_url: str,
    image_bytes: bytes,
    filename: str = "image.png",
    scale: int = 4,
    face_enhance: bool = True,
    model: str = "RealESRGAN_x4plus",
    denoise_strength: float = 0.5,
    timeout: int = 180,
) -> Tuple[bytes, Dict[str, Any]]:
    """Send image to Google Colab server for AI super-resolution / HD+ enhancement.
    
    Returns (enhanced_image_bytes, info_dict).
    """
    if not image_bytes:
        raise ValueError("Data gambar kosong!")

    health = check_colab_health(api_url)
    if not health["connected"]:
        raise ConnectionError(
            f"Koneksi ke Google Colab gagal: {health['message']}. "
            "Pastikan notebook Colab sedang berjalan dan URL tunnel masih aktif."
        )

    base_url = health["base_url"]
    endpoint = f"{base_url}/enhance-image"

    headers = {
        "User-Agent": "CustomTools-Enhancer-Client/1.0",
        "ngrok-skip-browser-warning": "true",
        "Bypass-Tunnel-Reminder": "true",
    }

    data = {
        "scale": str(scale),
        "face_enhance": "true" if face_enhance else "false",
        "model": str(model),
        "denoise_strength": str(denoise_strength),
    }

    files = {
        "file": (filename, image_bytes, "image/png"),
    }

    t0 = time.time()
    response = requests.post(
        endpoint,
        headers=headers,
        data=data,
        files=files,
        timeout=timeout,
    )
    elapsed = round(time.time() - t0, 2)

    if response.status_code != 200:
        err_msg = response.text[:300]
        try:
            err_json = response.json()
            if "detail" in err_json:
                err_msg = err_json["detail"]
        except Exception:
            pass
        raise RuntimeError(f"Server Colab mengembalikan error ({response.status_code}): {err_msg}")

    result_bytes = response.content
    if not result_bytes:
        raise RuntimeError("Server Colab mengembalikan data gambar kosong.")

    # Validate output image dimensions
    orig_dims = (0, 0)
    new_dims = (0, 0)
    try:
        with Image.open(io.BytesIO(image_bytes)) as img_in:
            orig_dims = img_in.size
        with Image.open(io.BytesIO(result_bytes)) as img_out:
            new_dims = img_out.size
    except Exception:
        pass

    info = {
        "status": "success",
        "elapsed_seconds": elapsed,
        "original_size_kb": round(len(image_bytes) / 1024, 1),
        "enhanced_size_kb": round(len(result_bytes) / 1024, 1),
        "original_dimensions": orig_dims,
        "enhanced_dimensions": new_dims,
        "scale": scale,
        "face_enhance": face_enhance,
        "model": model,
    }
    return result_bytes, info


def enhance_video_colab(
    api_url: str,
    video_bytes: bytes,
    filename: str = "video.mp4",
    scale: int = 2,
    face_enhance: bool = False,
    model: str = "realesr-animevideov3",
    timeout: int = 600,
) -> Tuple[bytes, Dict[str, Any]]:
    """Send video to Google Colab server for AI super-resolution / HD+ upscaling.
    
    Returns (enhanced_video_bytes, info_dict).
    """
    if not video_bytes:
        raise ValueError("Data video kosong!")

    health = check_colab_health(api_url)
    if not health["connected"]:
        raise ConnectionError(
            f"Koneksi ke Google Colab gagal: {health['message']}. "
            "Pastikan notebook Colab sedang berjalan dan URL tunnel masih aktif."
        )

    base_url = health["base_url"]
    endpoint = f"{base_url}/enhance-video"

    headers = {
        "User-Agent": "CustomTools-Enhancer-Client/1.0",
        "ngrok-skip-browser-warning": "true",
        "Bypass-Tunnel-Reminder": "true",
    }

    data = {
        "scale": str(scale),
        "face_enhance": "true" if face_enhance else "false",
        "model": str(model),
    }

    files = {
        "file": (filename, video_bytes, "video/mp4"),
    }

    t0 = time.time()
    response = requests.post(
        endpoint,
        headers=headers,
        data=data,
        files=files,
        timeout=timeout,
    )
    elapsed = round(time.time() - t0, 2)

    if response.status_code != 200:
        err_msg = response.text[:300]
        try:
            err_json = response.json()
            if "detail" in err_json:
                err_msg = err_json["detail"]
        except Exception:
            pass
        raise RuntimeError(f"Server Colab mengembalikan error ({response.status_code}): {err_msg}")

    result_bytes = response.content
    if not result_bytes:
        raise RuntimeError("Server Colab mengembalikan data video kosong.")

    info = {
        "status": "success",
        "elapsed_seconds": elapsed,
        "original_size_kb": round(len(video_bytes) / 1024, 1),
        "enhanced_size_kb": round(len(result_bytes) / 1024, 1),
        "scale": scale,
        "face_enhance": face_enhance,
        "model": model,
    }
    return result_bytes, info
