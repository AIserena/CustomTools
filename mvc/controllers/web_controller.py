"""Controllers for Streamlit workflows."""

from mvc.models import PdfAllMergeModel, PdfMergeModel


class WebController:
    """Coordinates web input with PDF models."""

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
