"""Model facade for removing image backgrounds and exporting results."""

from typing import Tuple

from mvc.models.background_remover_operations import (
    export_image,
    make_preview,
    remove_image_background,
)


class BackgroundRemoverModel:
    """Application-facing API for local AI background removal."""

    @staticmethod
    def remove_background(image_bytes: bytes) -> bytes:
        return remove_image_background(image_bytes)

    @staticmethod
    def export(
        image_bytes: bytes,
        output_format: str,
        background_color: str = "#FFFFFF",
        preserve_transparency: bool = False,
    ) -> Tuple[bytes, str, str]:
        return export_image(
            image_bytes=image_bytes,
            output_format=output_format,
            background_color=background_color,
            preserve_transparency=preserve_transparency,
        )

    @staticmethod
    def preview(
        image_bytes: bytes,
        background_color: str = "#FFFFFF",
        preserve_transparency: bool = False,
    ) -> bytes:
        return make_preview(
            image_bytes=image_bytes,
            background_color=background_color,
            preserve_transparency=preserve_transparency,
        )
