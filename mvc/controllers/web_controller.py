"""Controllers for Streamlit workflows."""

from mvc.models import CodeGeneratorModel, PdfAllMergeModel, PdfMergeModel, PdfToWordModel


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
    def generate_code(
        content: str,
        code_type: str,
        foreground: str = "#000000",
        background: str = "#FFFFFF",
        qr_size_cm: float = 4.0,
    ) -> bytes:
        return CodeGeneratorModel.generate(
            content=content,
            code_type=code_type,
            foreground=foreground,
            background=background,
            qr_size_cm=qr_size_cm,
        )
