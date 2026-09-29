"""QR code and Code 128 barcode image generation."""

import io

import barcode
import qrcode
from PIL import Image, ImageColor
from barcode.writer import ImageWriter
from qrcode.constants import ERROR_CORRECT_M
from qrcode.exceptions import DataOverflowError


CODE_TYPES = ("QR Code", "Barcode (Code 128)")
QR_SIZE_PRESETS = {
    "2 × 2 cm": 2.0,
    "3 × 3 cm": 3.0,
    "4 × 4 cm": 4.0,
    "5 × 5 cm": 5.0,
    "6 × 6 cm": 6.0,
    "1R — QR 6,35 × 6,35 cm": 6.35,
}
QR_BORDER = 4
QR_PRINT_DPI = 300


def _normalize_color(color: str, field_name: str) -> str:
    try:
        red, green, blue = ImageColor.getrgb(color)[:3]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Warna {field_name} tidak valid: {color}") from exc
    return f"#{red:02X}{green:02X}{blue:02X}"


def generate_code_image(
    content: str,
    code_type: str,
    foreground: str = "#000000",
    background: str = "#FFFFFF",
    qr_size_cm: float = 4.0,
) -> bytes:
    """Generate a QR code or Code 128 barcode as PNG bytes."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Konten QR/barcode tidak boleh kosong.")
    if code_type not in CODE_TYPES:
        raise ValueError(f"Jenis kode tidak didukung: {code_type}")
    if not isinstance(qr_size_cm, (int, float)) or not 0 < qr_size_cm <= 10:
        raise ValueError("Ukuran QR harus lebih dari 0 cm dan maksimal 10 cm.")

    foreground_color = _normalize_color(foreground, "depan")
    background_color = _normalize_color(background, "latar")
    image_buffer = io.BytesIO()

    if code_type == "QR Code":
        target_pixels = round(qr_size_cm / 2.54 * QR_PRINT_DPI)
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=1,
            border=QR_BORDER,
        )
        qr.add_data(content.encode("utf-8"), optimize=0)
        try:
            qr.make(fit=True)
        except DataOverflowError as exc:
            raise ValueError("Konten terlalu panjang untuk dibuat menjadi QR code.") from exc
        total_modules = len(qr.get_matrix())
        pixels_per_module = target_pixels // total_modules
        if pixels_per_module < 2:
            raise ValueError(
                f"Konten terlalu panjang untuk QR {qr_size_cm:g} cm agar tetap mudah dipindai. "
                "Silakan pilih ukuran QR yang lebih besar."
            )
        qr.box_size = pixels_per_module
        qr_image = qr.make_image(
            fill_color=foreground_color,
            back_color=background_color,
        ).get_image()
        image = Image.new("RGB", (target_pixels, target_pixels), background_color)
        image_position = (
            (target_pixels - qr_image.width) // 2,
            (target_pixels - qr_image.height) // 2,
        )
        image.paste(qr_image, image_position)
        image.save(image_buffer, format="PNG", dpi=(QR_PRINT_DPI, QR_PRINT_DPI))
    else:
        try:
            content.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError(
                "Barcode Code 128 hanya mendukung karakter ASCII. Gunakan QR Code untuk teks Unicode."
            ) from exc
        try:
            code = barcode.get("code128", content, writer=ImageWriter())
            code.write(
                image_buffer,
                options={
                    "background": background_color,
                    "foreground": foreground_color,
                    "write_text": True,
                    "module_width": 0.25,
                    "module_height": 15.0,
                    "quiet_zone": 6.5,
                    "font_size": 10,
                    "text_distance": 5.0,
                },
            )
        except (UnicodeEncodeError, ValueError) as exc:
            raise ValueError(f"Konten tidak didukung untuk Barcode Code 128: {exc}") from exc
        except Exception as exc:
            raise ValueError(f"Gagal membuat barcode: {exc}") from exc

    return image_buffer.getvalue()
