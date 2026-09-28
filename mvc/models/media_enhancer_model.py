"""Model facade for HD+ Video and Photo AI enhancement."""

from typing import Any, Dict, Tuple
from mvc.models.media_enhancer_operations import (
    check_colab_health,
    enhance_image_colab,
    enhance_video_colab,
)


class MediaEnhancerModel:
    """Application-facing API for HD+ Video and Photo AI enhancement via Google Colab."""

    @staticmethod
    def ping_colab(api_url: str, timeout: int = 6) -> Dict[str, Any]:
        """Check if the Colab enhancement server is reachable."""
        return check_colab_health(api_url, timeout=timeout)

    @staticmethod
    def enhance_image(
        api_url: str,
        image_bytes: bytes,
        filename: str = "image.png",
        scale: int = 4,
        face_enhance: bool = True,
        model: str = "RealESRGAN_x4plus",
        denoise_strength: float = 0.5,
        timeout: int = 180,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Enhance an image via Google Colab."""
        return enhance_image_colab(
            api_url=api_url,
            image_bytes=image_bytes,
            filename=filename,
            scale=scale,
            face_enhance=face_enhance,
            model=model,
            denoise_strength=denoise_strength,
            timeout=timeout,
        )

    @staticmethod
    def enhance_video(
        api_url: str,
        video_bytes: bytes,
        filename: str = "video.mp4",
        scale: int = 2,
        face_enhance: bool = False,
        model: str = "realesr-animevideov3",
        timeout: int = 600,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Enhance a video via Google Colab."""
        return enhance_video_colab(
            api_url=api_url,
            video_bytes=video_bytes,
            filename=filename,
            scale=scale,
            face_enhance=face_enhance,
            model=model,
            timeout=timeout,
        )


__all__ = ["MediaEnhancerModel"]
