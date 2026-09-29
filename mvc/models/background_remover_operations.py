"""Image background removal and export operations."""

import io
import math
from typing import Tuple

from PIL import Image, ImageColor


SUPPORTED_FORMATS = {
    "PNG": ("PNG", "image/png"),
    "JPG": ("JPEG", "image/jpeg"),
    "JPEG": ("JPEG", "image/jpeg"),
    "ICO": ("ICO", "image/x-icon"),
    "WEBP": ("WEBP", "image/webp"),
    "BMP": ("BMP", "image/bmp"),
    "TIFF": ("TIFF", "image/tiff"),
}

TRANSPARENT_FORMATS = {"PNG", "ICO", "WEBP", "TIFF"}


def estimate_removal_progress(elapsed_seconds: float) -> int:
    """Estimate progress while rembg runs, whose inference API has no progress callback."""
    elapsed = max(0.0, elapsed_seconds)
    return min(95, round(10 + 85 * (1 - math.exp(-elapsed / 20))))


def remove_image_background(image_bytes: bytes) -> bytes:
    """Remove an image background and return a transparent PNG."""
    if not image_bytes:
        raise ValueError("Data gambar kosong.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()
    except Exception as exc:
        raise ValueError(f"File bukan gambar yang valid: {exc}") from exc

    try:
        from rembg import remove
    except ImportError as exc:
        raise RuntimeError(
            "Modul remove BG belum terpasang. Instal dependensi dengan "
            "`pip install \"rembg[cpu]\"`, lalu jalankan ulang aplikasi."
        ) from exc

    result = remove(image_bytes)
    if not isinstance(result, bytes):
        raise RuntimeError("Model remove BG tidak mengembalikan data gambar dalam format byte.")
    try:
        with Image.open(io.BytesIO(result)) as image:
            output = image.convert("RGBA")
            buffer = io.BytesIO()
            output.save(buffer, format="PNG")
    except Exception as exc:
        raise RuntimeError(f"Model remove BG menghasilkan gambar yang tidak valid: {exc}") from exc
    return buffer.getvalue()


def export_image(
    image_bytes: bytes,
    output_format: str,
    background_color: str = "#FFFFFF",
    preserve_transparency: bool = False,
) -> Tuple[bytes, str, str]:
    """Encode a transparent PNG using a supported image format."""
    normalized_format = output_format.upper().lstrip(".")
    if normalized_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Format gambar tidak didukung: {output_format}")

    pil_format, mime_type = SUPPORTED_FORMATS[normalized_format]
    try:
        rgb_background = ImageColor.getrgb(background_color)
    except ValueError as exc:
        raise ValueError(f"Warna latar tidak valid: {background_color}") from exc

    with Image.open(io.BytesIO(image_bytes)) as image:
        rgba_image = image.convert("RGBA")

    keep_alpha = preserve_transparency and normalized_format in TRANSPARENT_FORMATS
    if keep_alpha:
        output_image = rgba_image
    else:
        background = Image.new("RGBA", rgba_image.size, (*rgb_background, 255))
        output_image = Image.alpha_composite(background, rgba_image)
        if pil_format in {"JPEG", "BMP"}:
            output_image = output_image.convert("RGB")

    buffer = io.BytesIO()
    if pil_format == "ICO":
        icon_side = max(16, min(max(rgba_image.size), 256))
        output_image.thumbnail((icon_side, icon_side), Image.Resampling.LANCZOS)
        canvas_color = (0, 0, 0, 0) if keep_alpha else (*rgb_background, 255)
        icon_image = Image.new("RGBA", (icon_side, icon_side), canvas_color)
        icon_position = (
            (icon_side - output_image.width) // 2,
            (icon_side - output_image.height) // 2,
        )
        icon_image.paste(output_image, icon_position)
        icon_sizes = [(size, size) for size in (16, 32, 48, 64, 128, 256) if size <= icon_side]
        icon_image.save(buffer, format="ICO", sizes=icon_sizes)
    elif pil_format == "JPEG":
        output_image.save(buffer, format=pil_format, quality=95)
    elif pil_format == "WEBP":
        output_image.save(buffer, format=pil_format, quality=95)
    else:
        output_image.save(buffer, format=pil_format)

    return buffer.getvalue(), mime_type, f".{normalized_format.lower()}"


def make_preview(
    image_bytes: bytes,
    background_color: str = "#FFFFFF",
    preserve_transparency: bool = False,
) -> bytes:
    """Create a PNG preview with the selected background settings."""
    preview, _, _ = export_image(
        image_bytes=image_bytes,
        output_format="PNG",
        background_color=background_color,
        preserve_transparency=preserve_transparency,
    )
    return preview
