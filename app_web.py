import os
import time
import datetime
import streamlit as st
import streamlit.components.v1 as components
from pdf_logic import proses_merge_pdf_memory, buat_zip_bytes
from pdf_all_logic import gabung_pdf_all_memory

# --- 1. KOMPONEN CUSTOM DRAG & DROP ---
_component_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drag_drop_component")
drag_drop_sortable = components.declare_component("drag_drop_sortable", path=_component_path)

# --- 2. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="CUSTOM TOOLS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. SIDEBAR BRANDING & NAVIGASI ---
with st.sidebar:
    st.title("CUSTOM")
    st.markdown("")
    st.caption("CUSTOM TOOLS")
    st.divider()

    st.markdown("#### **MENU:**")
    menu = st.radio(
        "Navigasi",
        options=[
            "📄 Penggabung PDF (by NIK)",
            "📑 Penggabung PDF (by All)",
            "🔒 Tool Lain (Segera Hadir)"
        ],
        label_visibility="collapsed"
    )

# Tracking popup per menu (reset saat ganti menu)
if "popup_last_menu" not in st.session_state:
    st.session_state["popup_last_menu"] = None
    st.session_state["popup_dismissed"] = False
    st.session_state["popup_closing"] = False

if st.session_state["popup_last_menu"] != menu:
    st.session_state["popup_last_menu"] = menu
    st.session_state["popup_dismissed"] = False
    st.session_state["popup_closing"] = False

PANDUAN = {
    "📄 Penggabung PDF (by NIK)": {
        "judul": "💡 Panduan: Penggabung PDF (by NIK)",
        "isi": """
**Cara Penggunaan:**
1. 📤 **Upload** semua file PDF — sistem otomatis mengelompokkan berdasarkan **NIK / ID Karyawan**.
2. ✏️ Isi **Urutan Kata Kunci** (dipisahkan koma) untuk menentukan urutan halaman. Misal: `1, 2` atau `Maret, April`.
3. ✏️ Isi **Nama File Lanjutan** untuk penamaan file hasil. NIK otomatis di depan. Misal: `_SLIP_GAJI` → hasil: `12345_SLIP_GAJI.pdf`.
4. 🚀 Klik **GABUNGKAN PDF** — proses otomatis berjalan.
5. 📦 Klik **DOWNLOAD SEMUA (.ZIP)** untuk mengunduh semua hasil sekaligus.
"""
    },
    "📑 Penggabung PDF (by All)": {
        "judul": "💡 Panduan: Penggabung PDF (by All)",
        "isi": """
**Cara Penggunaan:**
1. 📤 **Upload** file-file PDF yang ingin digabungkan menjadi **1 file tunggal**.
2. ✋ **Klik & Seret (DRAG)** kartu file ke atas atau ke bawah untuk menentukan urutan halaman. File paling atas = halaman 1.
3. ✏️ Isi **Nama File PDF Hasil Gabungan**.
4. 🚀 Klik **GABUNGKAN SEMUA PDF** — semua file digabung sesuai urutan drag.
5. ⬇️ Klik tombol **DOWNLOAD** untuk mengunduh file hasil.
"""
    },
}


def tampilkan_popup_panduan(menu_key: str):
    """Tampilkan popup panduan di atas halaman jika belum di-dismiss."""
    if st.session_state.get("popup_dismissed") and not st.session_state.get("popup_closing"):
        return
    if menu_key not in PANDUAN:
        return

    panduan = PANDUAN[menu_key]
    animasi = "custom-guide-fade-out" if st.session_state.get("popup_closing") else "custom-guide-fade-in"
    st.markdown(
        f"""
        <style>
        @keyframes customGuideFadeIn {{
            from {{ opacity: 0; transform: translateY(-8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes customGuideFadeOut {{
            from {{ opacity: 1; transform: translateY(0); }}
            to {{ opacity: 0; transform: translateY(-8px); }}
        }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            animation: {animasi} 350ms ease-out both;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):
        col_title, col_close = st.columns([9, 1])
        with col_title:
            st.markdown(f"#### {panduan['judul']}")
        with col_close:
            if st.button("✖", key="btn_close_popup", help="Tutup panduan ini"):
                st.session_state["popup_closing"] = True
                st.rerun()
        st.markdown(panduan["isi"])
    st.write("")

    if st.session_state.get("popup_closing"):
        time.sleep(0.35)
        st.session_state["popup_dismissed"] = True
        st.session_state["popup_closing"] = False
        st.rerun()


# --- 4. KONTEN UTAMA: PENGGABUNG PDF (BY NIK) ---
if menu == "📄 Penggabung PDF (by NIK)":
    tampilkan_popup_panduan("📄 Penggabung PDF (by NIK)")
    st.title("📄 Penggabung PDF Otomatis (by NIK)")
    st.markdown(
        "Mengelompokkan file PDF berdasarkan **NIK / ID Karyawan** dan mengurutkan halaman "
        "berdasarkan **kata kunci** yang ditentukan."
    )
    st.divider()


    st.subheader("1. Upload File PDF")
    uploaded_files = st.file_uploader(
        "Pilih atau seret (drag & drop) file-file PDF ke area di bawah ini:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Anda dapat memilih banyak file sekaligus (Ctrl + A lalu seret ke sini)",
        key="uploader_nik"
    )

    if uploaded_files:
        st.info(f"📁 Terdeteksi **{len(uploaded_files)}** file PDF siap diproses.")

    st.subheader("2. Pengaturan Penggabungan")
    col1, col2 = st.columns(2)

    with col1:
        kata_kunci = st.text_input(
            "Urutan Kata Kunci (Dipisahkan Koma):",
            value="1, 2, Oktober, November",
            help="Kata kunci di sebelah kiri akan menjadi halaman lebih depan. Contoh: 1, 2 atau Maret, April",
            key="kw_nik"
        )
        st.caption("*Contoh: `1, 2` atau `Maret, April`")

    with col2:
        penamaan_lanjutan = st.text_input(
            "Nama File Lanjutan (Setelah NIK):",
            value="_merged",
            help="NIK otomatis di depan. Contoh: jika diisi _SLIP_GAJI, maka hasil: NIK_SLIP_GAJI.pdf",
            key="nama_nik"
        )
        st.caption("*NIK otomatis di depan. Contoh: `_SLIP_GAJI` atau `- PKWT` (Hasil: `[NIK]_SLIP_GAJI.pdf`)")

    st.write("")
    tombol_proses = st.button("🚀 GABUNGKAN PDF", type="primary", use_container_width=True, key="btn_nik")

    if "hasil_merge" not in st.session_state:
        st.session_state["hasil_merge"] = None
        st.session_state["laporan"] = None
        st.session_state["unpaired"] = None

    if tombol_proses:
        if not uploaded_files:
            st.error("⚠️ Harap upload setidaknya 2 file PDF terlebih dahulu!")
        else:
            with st.spinner("Sedang memproses dan menggabungkan file PDF..."):
                files_dict = {f.name: f.getvalue() for f in uploaded_files}
                hasil_dict, laporan, unpaired = proses_merge_pdf_memory(
                    files_dict, kata_kunci, penamaan_lanjutan
                )

                st.session_state["hasil_merge"] = hasil_dict
                st.session_state["laporan"] = laporan
                st.session_state["unpaired"] = unpaired

    if st.session_state["hasil_merge"] is not None:
        hasil_dict = st.session_state["hasil_merge"]
        laporan = st.session_state["laporan"]
        unpaired = st.session_state["unpaired"]

        st.divider()
        if hasil_dict:
            st.success(f"🎉 **Selesai!** Berhasil menggabungkan **{len(hasil_dict)} pasang** file PDF.")

            zip_bytes = buat_zip_bytes(hasil_dict)
            waktu_sekarang = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nama_zip = f"HASIL_MERGE_PDF_{waktu_sekarang}.zip"

            st.download_button(
                label=f"📦 DOWNLOAD SEMUA HASIL ({len(hasil_dict)} FILE - .ZIP)",
                data=zip_bytes,
                file_name=nama_zip,
                mime="application/zip",
                type="primary",
                use_container_width=True
            )

            st.write("")
            tab_hasil, tab_unpaired = st.tabs(["📋 Rincian File yang Berhasil Digabung", "⚠️ File Tanpa Pasangan"])

            with tab_hasil:
                for item in laporan:
                    with st.expander(f"📄 **{item['output']}** (NIK: `{item['nik']}`) — {item['size_kb']} KB"):
                        st.write(f"**Jumlah file asal:** {item['count']}")
                        st.write("**File asal yang digabung:**")
                        for f in item["files"]:
                            st.write(f"- {f}")
                        
                        st.download_button(
                            label=f"⬇️ Download {item['output']}",
                            data=hasil_dict[item['output']],
                            file_name=item['output'],
                            mime="application/pdf",
                            key=f"dl_{item['output']}"
                        )

            with tab_unpaired:
                if unpaired:
                    st.warning(
                        f"Ditemukan **{len(unpaired)}** file yang tidak memiliki pasangan NIK yang sama:"
                    )
                    for f in unpaired:
                        st.write(f"- `{f}`")
                else:
                    st.info("Semua file PDF yang diupload memiliki pasangan NIK dan berhasil digabungkan.")
        else:
            st.warning("⚠️ Tidak ditemukan file PDF dengan pasangan 4-digit ID/NIK yang sama.")
            if unpaired:
                st.write("**File yang terdeteksi:**")
                for f in unpaired:
                    st.write(f"- `{f}`")


# --- 5. KONTEN UTAMA: PENGGABUNG PDF (BY ALL) DENGAN DRAG & DROP ---
elif menu == "📑 Penggabung PDF (by All)":
    tampilkan_popup_panduan("📑 Penggabung PDF (by All)")
    st.title("📑 Penggabung PDF (by All)")
    st.markdown(
        "Menggabungkan seluruh file PDF yang dipilih menjadi **1 file dokumen utuh**. "
        "Anda dapat **mengklik dan menyeret (DRAG)** posisi file di bawah untuk menentukan halaman mana yang pertama, kedua, dan seterusnya."
    )
    st.divider()

    st.subheader("1. Upload File PDF")
    uploaded_all = st.file_uploader(
        "Upload file-file PDF yang ingin digabungkan:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Pilih 2 atau lebih file PDF untuk digabungkan menjadi 1 file",
        key="uploader_all"
    )

    if uploaded_all:
        total_files = len(uploaded_all)
        st.info(f"📁 Terdeteksi **{total_files}** file PDF.")

        # Inisialisasi daftar urutan index jika belum ada atau jumlah file berubah
        if "order_indices" not in st.session_state or len(st.session_state["order_indices"]) != total_files:
            st.session_state["order_indices"] = list(range(total_files))

        current_indices = st.session_state["order_indices"]

        st.subheader("2. Atur Urutan Halaman (Klik & Seret / Drag)")
        st.markdown(
            "💡 **Petunjuk:** Klik dan **seret (DRAG)** kartu file ke atas atau ke bawah untuk menukar urutan. "
            "File pada posisi paling atas (**#1**) akan menjadi halaman depan."
        )

        items_for_sort = [
            {
                "index": idx,
                "name": uploaded_all[idx].name,
                "size": round(len(uploaded_all[idx].getvalue()) / 1024, 1)
            }
            for idx in current_indices
        ]

        # Komponen Interaktif HTML5 Drag & Drop
        new_order = drag_drop_sortable(
            items=items_for_sort,
            default=current_indices,
            key=f"drag_sorter_key_{total_files}"
        )

        # Update urutan jika ada hasil drag yang valid
        if new_order and isinstance(new_order, list) and len(new_order) == total_files:
            st.session_state["order_indices"] = new_order

        active_indices = st.session_state["order_indices"]

        st.divider()
        st.subheader("3. Nama File Hasil & Gabungkan")

        col1, col2 = st.columns([3, 2])
        with col1:
            nama_file_gabungan = st.text_input(
                "Nama File PDF Hasil Gabungan:",
                value="Dokumen_Gabungan.pdf",
                help="Nama file PDF yang akan diunduh",
                key="nama_output_all"
            )
            if not nama_file_gabungan.lower().endswith(".pdf"):
                nama_file_gabungan += ".pdf"

        with col2:
            st.write("")
            st.write("")
            btn_gabung_all = st.button(
                "🚀 GABUNGKAN SEMUA PDF",
                type="primary",
                use_container_width=True,
                key="btn_all_submit"
            )

        # Proses saat tombol ditekan
        if btn_gabung_all:
            if total_files < 2:
                st.error("⚠️ Harap upload minimal 2 file PDF untuk digabungkan!")
            else:
                with st.spinner("Sedang menggabungkan semua file PDF sesuai urutan..."):
                    try:
                        ordered_tuples = [
                            (uploaded_all[idx].name, uploaded_all[idx].getvalue())
                            for idx in active_indices
                        ]
                        merged_bytes = gabung_pdf_all_memory(ordered_tuples)
                        st.session_state["hasil_merge_all"] = merged_bytes
                    except Exception as e:
                        st.error(f"Gagal menggabungkan PDF: {e}")

        # Tampilkan Tombol Download jika hasil sudah ada
        if st.session_state.get("hasil_merge_all") is not None:
            st.success(
                f"🎉 **Selesai!** Berhasil menggabungkan **{total_files} file** menjadi `{nama_file_gabungan}`."
            )
            st.download_button(
                label=f"⬇️ DOWNLOAD {nama_file_gabungan}",
                data=st.session_state["hasil_merge_all"],
                file_name=nama_file_gabungan,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    else:
        st.session_state["hasil_merge_all"] = None


# --- 6. KONTEN UTAMA: TOOL LAIN ---
elif menu == "🔒 Tool Lain (Segera Hadir)":
    st.title("🔒 Tool Lain")
    st.info("Fitur utilitas tambahan sedang dalam tahap pengembangan dan akan segera hadir.")
