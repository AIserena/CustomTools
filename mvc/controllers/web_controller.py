"""Controllers for Streamlit workflows."""

from mvc.models import (
    BackgroundRemoverModel,
    MediaEnhancerModel,
    PdfAllMergeModel,
    PdfMergeModel,
    PdfToWordModel,
)


class WebController:
    """Coordinates web input with models."""

    @staticmethod
    def merge_by_id(files, keywords, suffix):
        file_data = {file.name: file.getvalue() for file in files}
        return PdfMergeModel.merge_memory(file_data, keywords, suffix)

    @staticmethod
    def merge_all(files):
        file_data = [(file.name, file.getvalue()) for file in files]
        return PdfAllMergeModel.merge_memory(file_data)

    @staticmethod
    def create_zip(results):
        return PdfMergeModel.create_zip(results)

    @staticmethod
    def convert_pdf_to_word(file, pages_spec=None, delete_hyphen=True):
        return PdfToWordModel.convert_memory(
            pdf_bytes=file.getvalue(),
            pages_spec=pages_spec,
            delete_hyphen=delete_hyphen,
        )

    @staticmethod
    def convert_batch_pdf_to_word(files, pages_spec=None, delete_hyphen=True):
        file_tuples = [(file.name, file.getvalue()) for file in files]
        return PdfToWordModel.convert_batch_memory(
            files=file_tuples,
            pages_spec=pages_spec,
            delete_hyphen=delete_hyphen,
        )

    @staticmethod
    def ping_colab(api_url: str):
        return MediaEnhancerModel.ping_colab(api_url)

    @staticmethod
    def enhance_image(api_url: str, file, scale: int = 4, face_enhance: bool = True, model: str = "RealESRGAN_x4plus", denoise_strength: float = 0.5):
        return MediaEnhancerModel.enhance_image(
            api_url=api_url,
            image_bytes=file.getvalue(),
            filename=file.name,
            scale=scale,
            face_enhance=face_enhance,
            model=model,
            denoise_strength=denoise_strength,
        )

    @staticmethod
    def enhance_video(api_url: str, file, scale: int = 2, face_enhance: bool = False, model: str = "realesr-animevideov3"):
        return MediaEnhancerModel.enhance_video(
            api_url=api_url,
            video_bytes=file.getvalue(),
            filename=file.name,
            scale=scale,
            face_enhance=face_enhance,
            model=model,
        )

    @staticmethod
    def remove_background(image_bytes: bytes):
        return BackgroundRemoverModel.remove_background(image_bytes)

    @staticmethod
    def export_background_removed_image(
        image_bytes: bytes,
        output_format: str,
        background_color: str,
        preserve_transparency: bool,
    ):
        return BackgroundRemoverModel.export(
            image_bytes=image_bytes,
            output_format=output_format,
            background_color=background_color,
            preserve_transparency=preserve_transparency,
        )

    @staticmethod
    def preview_background_removed_image(
        image_bytes: bytes,
        background_color: str,
        preserve_transparency: bool,
    ):
        return BackgroundRemoverModel.preview(
            image_bytes=image_bytes,
            background_color=background_color,
            preserve_transparency=preserve_transparency,
        )
