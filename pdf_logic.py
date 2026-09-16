import os
import sys
import subprocess
import re
import io
import zipfile
from pypdf import PdfWriter

def hitung_pdf(folder_sumber):
    """Menghitung jumlah file PDF yang valid di dalam folder."""
    if not folder_sumber or not os.path.exists(folder_sumber):
        return 0
    return len([
        f for f in os.listdir(folder_sumber)
        if f.lower().endswith('.pdf') and not f.endswith('_merged.pdf')
    ])

def buat_nama_file(emp_id, penamaan_lanjutan="_merged"):
    """
    Menghasilkan nama file PDF hasil merge.
    - NIK (emp_id) otomatis dihasilkan.
    - penamaan_lanjutan dapat ditentukan sendiri oleh user.
    - Jika user menyertakan placeholder {NIK} / {nik}, maka akan diganti dengan emp_id.
    - Jika user hanya mengisi teks lanjutan (misal: '_SLIP_GAJI', ' - LAPORAN', 'REKAP'),
      maka otomatis NIK diletakkan di depan: {NIK}{penamaan_lanjutan}.pdf
    """
    if not penamaan_lanjutan or not str(penamaan_lanjutan).strip():
        penamaan_lanjutan = "_merged"

    teks = str(penamaan_lanjutan).strip()

    # Bersihkan ekstensi .pdf jika user tidak sengaja mengetiknya di input
    if teks.lower().endswith(".pdf"):
        teks = teks[:-4].rstrip()

    # Bersihkan karakter terlarang untuk nama file Windows: \ / : * ? " < > |
    teks = re.sub(r'[\\/*?:"<>|]', '', teks)

    if "{nik}" in teks.lower():
        pattern = re.compile(r'\{nik\}', re.IGNORECASE)
        nama = pattern.sub(emp_id, teks)
    else:
        # Jika tidak diawali tanda pemisah (_, -, spasi, titik), beri pemisah underscore
        if teks and not teks.startswith(('_', '-', ' ', '.')):
            nama = f"{emp_id}_{teks}"
        else:
            nama = f"{emp_id}{teks}"

    return f"{nama}.pdf"

def proses_merge_pdf(folder_sumber, folder_tujuan, kata_kunci_raw, penamaan_lanjutan="_merged"):
    """Memproses pengelompokan dan penggabungan PDF berdasarkan ID fleksibel (huruf/angka) & kata kunci."""
    if not folder_sumber or not folder_tujuan:
        raise ValueError("Harap pilih folder sumber dan folder tujuan!")

    # Ambil urutan kata kunci yang diinput user (pisahkan berdasarkan koma)
    keywords = [k.strip().lower() for k in kata_kunci_raw.split(',') if k.strip()]

    if not os.path.exists(folder_tujuan):
        os.makedirs(folder_tujuan)

    grouped_files = {}

    # 1. Kelompokkan file berdasarkan ID Unik (Bisa NIK 5 digit, diawali P/G, dsb)
    for file_name in os.listdir(folder_sumber):
        if file_name.lower().endswith('.pdf') and not file_name.endswith('_merged.pdf'):
            
            # REGEX BARU:
            # Mencari kata yang mengandung angka minimal 4 digit (bisa nempel huruf seperti P12345, G98765, 123456)
            match = re.search(r'\b([a-zA-Z]*\d{4,}[a-zA-Z0-9]*)\b', file_name)
            
            if match:
                emp_id = match.group(1).upper()  # Diseragamkan ke huruf kapital (misal: p12345 jadi P12345)
                if emp_id not in grouped_files:
                    grouped_files[emp_id] = []
                grouped_files[emp_id].append(file_name)

    total_gabung = 0

    # Fungsi penentu urutan file berdasarkan kata kunci
    def dapatkan_urutan(nama_file):
        nama_lower = nama_file.lower()
        if keywords:
            for index, kw in enumerate(keywords):
                if kw in nama_lower:
                    return index  # Indeks lebih kecil = halaman lebih depan
        
        # Pengaman jika kata kunci tidak cocok: cari angka di akhir nama file
        match_angka = re.search(r'(\d+)(?:\.pdf)?$', nama_file)
        if match_angka:
            return int(match_angka.group(1))
        return 999

    # 2. Urutkan dan gabungkan
    for emp_id, files in grouped_files.items():
        if len(files) > 1:
            files.sort(key=dapatkan_urutan)

            merger = PdfWriter()
            for pdf in files:
                pdf_path = os.path.join(folder_sumber, pdf)
                merger.append(pdf_path)

            nama_file_hasil = buat_nama_file(emp_id, penamaan_lanjutan)
            output_filename = os.path.join(folder_tujuan, nama_file_hasil)
            merger.write(output_filename)
            merger.close()
            total_gabung += 1

    return total_gabung

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

# Alias agar fleksibel dipanggil
buka_folder_hasil = buka_folder

def proses_merge_pdf_memory(files_dict, kata_kunci_raw, penamaan_lanjutan="_merged"):
    """
    Memproses penggabungan PDF dari memory/stream (untuk kebutuhan Web / Streamlit / API).
    files_dict: dict {filename: bytes}
    Returns:
        hasil_dict: dict {nama_file_output: bytes_pdf}
        laporan: list of dict [{"nik": emp_id, "output": nama_file_output, "count": len, "files": [...]}]
        unpaired: list of str nama file yang tidak memiliki pasangan 4-digit ID yang sama
    """
    keywords = [k.strip().lower() for k in kata_kunci_raw.split(',') if k.strip()]
    grouped_files = {}

    # 1. Kelompokkan file berdasarkan ID Unik (Bisa NIK 5 digit, diawali P/G, dsb)
    for file_name, file_bytes in files_dict.items():
        if file_name.lower().endswith('.pdf') and not file_name.endswith('_merged.pdf'):
            match = re.search(r'\b([a-zA-Z]*\d{4,}[a-zA-Z0-9]*)\b', file_name)
            if match:
                emp_id = match.group(1).upper()
                if emp_id not in grouped_files:
                    grouped_files[emp_id] = []
                grouped_files[emp_id].append((file_name, file_bytes))

    # Fungsi penentu urutan file berdasarkan kata kunci
    def dapatkan_urutan(nama_file):
        nama_lower = nama_file.lower()
        if keywords:
            for index, kw in enumerate(keywords):
                if kw in nama_lower:
                    return index
        match_angka = re.search(r'(\d+)(?:\.pdf)?$', nama_file)
        if match_angka:
            return int(match_angka.group(1))
        return 999

    hasil_dict = {}
    laporan = []
    unpaired = []

    # 2. Urutkan dan gabungkan dalam memory
    for emp_id, files in grouped_files.items():
        if len(files) > 1:
            files.sort(key=lambda x: dapatkan_urutan(x[0]))

            merger = PdfWriter()
            for fname, fbytes in files:
                merger.append(io.BytesIO(fbytes))

            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()

            nama_file_hasil = buat_nama_file(emp_id, penamaan_lanjutan)
            pdf_bytes = output_buffer.getvalue()
            hasil_dict[nama_file_hasil] = pdf_bytes

            laporan.append({
                "nik": emp_id,
                "output": nama_file_hasil,
                "count": len(files),
                "files": [f[0] for f in files],
                "size_kb": round(len(pdf_bytes) / 1024, 1)
            })
        else:
            unpaired.extend([f[0] for f in files])

    return hasil_dict, laporan, unpaired

def buat_zip_bytes(hasil_dict):
    """Mengemas semua file PDF hasil merge ke dalam satu arsip ZIP di memory."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, fbytes in hasil_dict.items():
            zf.writestr(fname, fbytes)
    return zip_buffer.getvalue()