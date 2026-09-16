import os
import sys
import subprocess
import io
from pypdf import PdfWriter

def gabung_pdf_all_files(list_file_paths, output_filepath):
    """
    Menggabungkan semua file PDF sesuai urutan list_file_paths menjadi 1 file PDF.
    Digunakan untuk antarmuka Desktop.
    """
    if not list_file_paths:
        raise ValueError("Daftar file PDF tidak boleh kosong!")

    if len(list_file_paths) < 2:
        raise ValueError("Pilih setidaknya 2 file PDF untuk digabungkan!")

    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    merger = PdfWriter()
    for path in list_file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File tidak ditemukan: {path}")
        merger.append(path)

    merger.write(output_filepath)
    merger.close()
    return output_filepath

def gabung_pdf_all_memory(list_file_tuples):
    """
    Menggabungkan semua file PDF dari memory/stream (untuk Web/Streamlit).
    list_file_tuples: list of tuple (filename, bytes) sesuai urutan yang diinginkan.
    Returns: bytes dari file PDF gabungan.
    """
    if not list_file_tuples:
        raise ValueError("Daftar file PDF tidak boleh kosong!")

    if len(list_file_tuples) < 2:
        raise ValueError("Upload setidaknya 2 file PDF untuk digabungkan!")

    merger = PdfWriter()
    for fname, fbytes in list_file_tuples:
        merger.append(io.BytesIO(fbytes))

    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    return output_buffer.getvalue()

def buka_folder(folder_path):
    """Membuka folder di file explorer sistem (Windows / macOS / Linux)."""
    if not folder_path:
        raise ValueError("Harap tentukan path folder terlebih dahulu!")

    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    if os.name == 'nt':
        os.startfile(folder_path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', folder_path])
    else:
        subprocess.Popen(['xdg-open', folder_path])

