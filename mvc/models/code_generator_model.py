"""Model facade for QR code and barcode generation."""

from mvc.models.code_generator_operations import (
    QR_SIZE_PRESETS as _QR_SIZE_PRESETS,
    generate_code_image,
)


class CodeGeneratorModel:
    """Application-facing API for generating QR and Code 128 images."""

    QR_SIZE_PRESETS = _QR_SIZE_PRESETS

    @staticmethod
    def generate(
        content: str,
        code_type: str,
        foreground: str = "#000000",
        background: str = "#FFFFFF",
        qr_size_cm: float = 4.0,
    ) -> bytes:
        return generate_code_image(
            content=content,
            code_type=code_type,
            foreground=foreground,
            background=background,
            qr_size_cm=qr_size_cm,
        )
