import os
import datetime
import hashlib
import threading
import time
import streamlit as st
import streamlit.components.v1 as components
from mvc.controllers import WebController
from mvc.views.web_guide import show_guide

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
            "📝 Konversi PDF ke Word",
            "✨ HD+ Video & Foto (Colab AI)",
            "🖼️ Remove Background",
            "🔒 Tool Lain (Segera Hadir)"
        ],
        label_visibility="collapsed"
    )

# Tracking popup per menu (reset saat ganti menu)
if "popup_last_menu" not in st.session_state:
    st.session_state["popup_last_menu"] = None
    st.session_state["popup_dismissed"] = False
if st.session_state["popup_last_menu"] != menu:
    st.session_state["popup_last_menu"] = menu
    st.session_state["popup_dismissed"] = False

# --- 4. KONTEN UTAMA: PENGGABUNG PDF (BY NIK) ---
if menu == "📄 Penggabung PDF (by NIK)":
    if not st.session_state.get("popup_dismissed"):
        show_guide("📄 Penggabung PDF (by NIK)")
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
                hasil_dict, laporan, unpaired = WebController.merge_by_id(
                    uploaded_files, kata_kunci, penamaan_lanjutan
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

            zip_bytes = WebController.create_zip(hasil_dict)
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
    if not st.session_state.get("popup_dismissed"):
        show_guide("📑 Penggabung PDF (by All)")
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
                        ordered_files = [uploaded_all[idx] for idx in active_indices]
                        merged_bytes = WebController.merge_all(ordered_files)
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


# --- 6. KONTEN UTAMA: KONVERSI PDF KE WORD (.DOCX RAPIH) ---
elif menu == "📝 Konversi PDF ke Word":
    if not st.session_state.get("popup_dismissed"):
        show_guide("📝 Konversi PDF ke Word")

    st.title("📝 Konversi PDF ke Word (.docx)")
    st.markdown(
        "Mengonversi file dokumen PDF menjadi dokumen **Microsoft Word (.docx)** dengan **tata letak rapi, "
        "format font terjaga, dan tabel yang dapat diedit langsung** (bukan sekadar textbox berantakan)."
    )
    st.divider()

    st.subheader("1. Upload File PDF")
    uploaded_pdf_list = st.file_uploader(
        "Pilih atau seret (drag & drop) file-file PDF ke area di bawah ini:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Mendukung konversi satu file maupun banyak file sekaligus",
        key="uploader_pdf_to_word"
    )

    if uploaded_pdf_list:
        st.info(f"📁 Terdeteksi **{len(uploaded_pdf_list)}** file PDF siap dikonversi.")

    st.subheader("2. Pengaturan Kerapihan Dokumen")
    col_w1, col_w2 = st.columns(2)

    with col_w1:
        rentang_halaman = st.text_input(
            "Rentang Halaman (Opsional):",
            value="",
            placeholder="Contoh: 1-3, 5 atau kosongkan untuk Semua",
            help="Kosongkan jika ingin mengonversi seluruh halaman dokumen PDF.",
            key="pages_pdf_to_word"
        )
        st.caption("*Kosongkan untuk **Semua Halaman**, atau ketik misal: `1-5` atau `1, 3, 5-7`")

    with col_w2:
        st.write("**Opsi Rekonstruksi Layout:**")
        opt_hyphen = st.checkbox(
            "Rapihkan spasi & tanda hubung akhir baris (hyphenation)",
            value=True,
            help="Menghilangkan pemenggalan kata otomatis pada akhir baris agar teks menyatu alami.",
            key="chk_hyphen"
        )
        st.caption("✨ *Tabel garis batas, tabel teks selaras, dan daftar poin (bullet list) otomatis direkonstruksi menjadi format Word asli.*")

    st.write("")
    btn_convert_word = st.button(
        "🚀 KONVERSI KE WORD (.DOCX)",
        type="primary",
        use_container_width=True,
        key="btn_convert_pdf_to_word"
    )

    if "hasil_pdf_to_word" not in st.session_state:
        st.session_state["hasil_pdf_to_word"] = None
        st.session_state["laporan_pdf_to_word"] = None

    if btn_convert_word:
        if not uploaded_pdf_list:
            st.error("⚠️ Harap upload setidaknya 1 file PDF terlebih dahulu!")
        else:
            with st.spinner("Sedang memproses dan merekonstruksi dokumen PDF ke format Word (.docx)..."):
                try:
                    hasil_dict, laporan = WebController.convert_batch_pdf_to_word(
                        files=uploaded_pdf_list,
                        pages_spec=rentang_halaman,
                        delete_hyphen=opt_hyphen
                    )
                    st.session_state["hasil_pdf_to_word"] = hasil_dict
                    st.session_state["laporan_pdf_to_word"] = laporan
                except Exception as exc:
                    st.error(f"Gagal melakukan konversi: {exc}")

    if st.session_state.get("hasil_pdf_to_word") is not None:
        hasil_word = st.session_state["hasil_pdf_to_word"]
        laporan_word = st.session_state["laporan_pdf_to_word"]

        st.divider()
        if hasil_word:
            sukses_count = sum(1 for item in laporan_word if item.get("status") == "success")
            st.success(f"🎉 **Selesai!** Berhasil mengonversi **{sukses_count} file** menjadi dokumen Word (.docx) yang rapi.")

            # Jika lebih dari 1 file, sediakan download ZIP
            if len(hasil_word) > 1:
                zip_bytes = WebController.create_zip(hasil_word)
                waktu_sekarang = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nama_zip = f"HASIL_CONVERT_WORD_{waktu_sekarang}.zip"

                st.download_button(
                    label=f"📦 DOWNLOAD SEMUA HASIL ({len(hasil_word)} DOKUMEN WORD - .ZIP)",
                    data=zip_bytes,
                    file_name=nama_zip,
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
                st.write("")

            st.subheader("📋 Daftar Dokumen Hasil Konversi")
            for item in laporan_word:
                if item.get("status") == "success":
                    out_name = item["output"]
                    with st.expander(f"📄 **{out_name}** — {item['size_kb']} KB (Sumber: `{item['source']}`)", expanded=True):
                        st.write(f"✅ Format teks, tata letak, dan tabel berhasil direkonstruksi.")
                        st.download_button(
                            label=f"⬇️ Download {out_name}",
                            data=hasil_word[out_name],
                            file_name=out_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_word_{out_name}"
                        )
                else:
                    st.error(f"❌ Gagal mengonversi `{item['source']}`: {item.get('error')}")


# --- 7. KONTEN UTAMA: HD+ VIDEO & FOTO (INTEGRASI GOOGLE COLAB GPU) ---
elif menu == "✨ HD+ Video & Foto (Colab AI)":
    if not st.session_state.get("popup_dismissed"):
        show_guide("✨ HD+ Video & Foto (Colab AI)")

    st.title("✨ HD+ Video & Foto (AI Super Resolution)")
    st.markdown(
        "Tingkatkan resolusi dan kejernihan foto & video menjadi **HD / 4K**, pertajam detail wajah (*Face Restoration*), "
        "dan hilangkan bintik/noise dengan tenaga akselerasi **GPU Google Colab (Gratis T4)**."
    )
    st.divider()

    # --- PENGATURAN KONEKSI GOOGLE COLAB ---
    st.subheader("1. Koneksi API Google Colab")

    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        colab_url = st.text_input(
            "URL API Google Colab (Cloudflare / ngrok):",
            value=st.session_state.get("colab_api_url", ""),
            placeholder="Contoh: https://xxxx-xxxx.trycloudflare.com",
            help="Masukkan public URL yang dihasilkan dari script server di Google Colab",
            key="input_colab_url"
        )
    with col_c2:
        st.write("")
        st.write("")
        btn_ping = st.button("🔌 Tes Koneksi", use_container_width=True, key="btn_ping_colab")

    if colab_url:
        st.session_state["colab_api_url"] = colab_url.strip()

    if btn_ping:
        if not colab_url:
            st.warning("⚠️ Harap isi URL Google Colab terlebih dahulu!")
        else:
            with st.spinner("Menghubungkan ke Google Colab..."):
                health = WebController.ping_colab(colab_url)
                if health["connected"]:
                    gpu_info = health.get("details", {}).get("gpu", "GPU Aktif")
                    st.success(f"🟢 **Terhubung!** Server Google Colab aktif ({gpu_info}).")
                else:
                    st.error(f"🔴 **Gagal terhubung:** {health.get('message')}")

    with st.expander("📖 **Cara Menjalankan Server di Google Colab (GPU T4 Gratis)**", expanded=False):
        st.markdown(
            """
            **Langkah Mudah:**
            1. Buka [Google Colab](https://colab.research.google.com) → Buat **New Notebook**.
            2. Ubah tipe runtime ke GPU: **Runtime > Change runtime type > T4 GPU > Save**.
            3. Salin kode Python di bawah ini, paste ke dalam 1 cell, klik **Run (▶)**.
            4. Tunggu 1–2 menit hingga muncul URL: `https://xxxx-xxxx.trycloudflare.com`.
            5. Salin URL tersebut dan tempel ke kolom di atas!
            """
        )
        try:
            with open("colab_server_script.py", "r", encoding="utf-8") as f_script:
                script_code = f_script.read()
            st.code(script_code, language="python")
        except Exception:
            st.caption("Lihat file `colab_server_script.py` di root direktori proyek.")

    st.divider()
    st.subheader("2. Pilih Media & Opsi HD+")

    tab_foto, tab_video = st.tabs(["📸 Peningkatan Foto (Image HD+)", "🎥 Peningkatan Video (Video HD+)"])

    # --- TAB 1: FOTO HD+ ---
    with tab_foto:
        uploaded_img = st.file_uploader(
            "Upload Foto / Gambar:",
            type=["jpg", "jpeg", "png", "webp"],
            help="Mendukung JPG, PNG, WEBP",
            key="uploader_foto_hd"
        )

        if uploaded_img:
            img_kb = round(uploaded_img.size / 1024, 1)
            st.success(f"✅ Foto siap diproses: **{uploaded_img.name}** ({img_kb} KB)")
            st.progress(1.0, text="Status Upload: 100% Selesai diterima browser")
        else:
            st.caption("ℹ️ Tips: Tunggu lingkaran putar di kotak upload selesai sebelum menekan tombol proses.")

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            scale_foto = st.selectbox(
                "Faktor Perbesaran Resolusi:",
                options=[4, 2],
                format_func=lambda x: f"{x}x — Ultra HD / 4K" if x == 4 else f"{x}x — High Definition",
                key="scale_foto"
            )
            model_foto = st.selectbox(
                "Model AI:",
                options=["RealESRGAN_x4plus", "realesr-general-x4v3", "realesr-animevideov3"],
                format_func=lambda m: (
                    "Real-ESRGAN (Detail Tajam Standar)" if "x4plus" in m
                    else ("Real-ESRGAN General (Foto & Denoise)" if "general" in m
                          else "Real-ESRGAN Anime / Ilustrasi")
                ),
                key="model_foto"
            )
        with col_opt2:
            face_enhance = st.checkbox(
                "Restorasi & Penajaman Detail Wajah",
                value=True,
                help="Memperjelas mata, hidung, bibir, dan tekstur wajah secara alami",
                key="face_foto"
            )
            denoise_val = st.slider(
                "Tingkat Pengurangan Bintik / Noise:",
                min_value=0.0, max_value=1.0, value=0.5, step=0.1,
                help="Membantu membersihkan foto lama atau foto berpiksel/buram",
                key="denoise_foto"
            )

        st.write("")
        btn_enhance_img = st.button(
            "🚀 TINGKATKAN KUALITAS FOTO (HD+)",
            type="primary", use_container_width=True, key="btn_run_foto"
        )

        if btn_enhance_img:
            if not colab_url:
                st.error("⚠️ Harap masukkan URL Google Colab pada langkah 1!")
            elif not uploaded_img:
                st.error("⚠️ Harap upload file foto terlebih dahulu!")
            else:
                result_container_img = {}

                def _worker_img():
                    try:
                        res_b, inf = WebController.enhance_image(
                            api_url=colab_url,
                            file=uploaded_img,
                            scale=scale_foto,
                            face_enhance=face_enhance,
                            model=model_foto,
                            denoise_strength=denoise_val,
                        )
                        result_container_img["data"] = (res_b, inf)
                    except Exception as exc:
                        result_container_img["error"] = exc

                t_img = threading.Thread(target=_worker_img)
                t_img.start()

                prog_img = st.progress(10, text="📤 [Tahap 1/3] Mengirim foto ke Google Colab...")
                start_img_t = time.time()
                while t_img.is_alive():
                    elapsed = round(time.time() - start_img_t, 1)
                    if elapsed < 2.5:
                        pct = min(45, int(10 + (elapsed / 2.5) * 35))
                        prog_img.progress(pct, text=f"📤 [Tahap 1/3] Mengirim foto ke GPU Colab... ({elapsed}s)")
                    elif elapsed < 7.0:
                        pct = min(85, int(45 + ((elapsed - 2.5) / 4.5) * 40))
                        prog_img.progress(pct, text=f"🧠 [Tahap 2/3] GPU Colab memproses AI Super Resolution & Face Restoration... ({elapsed}s)")
                    else:
                        pct = min(98, int(85 + (elapsed - 7.0) * 1.5))
                        prog_img.progress(pct, text=f"📥 [Tahap 3/3] Mengambil hasil foto HD+... ({elapsed}s)")
                    time.sleep(0.2)

                t_img.join()
                if "data" in result_container_img:
                    total_time = round(time.time() - start_img_t, 1)
                    prog_img.progress(100, text=f"✅ Foto HD+ Berhasil Selesai! ({total_time} detik)")
                    res_bytes, info = result_container_img["data"]
                    st.session_state["hasil_foto_hd"] = res_bytes
                    st.session_state["info_foto_hd"] = info
                    st.session_state["nama_foto_asli"] = uploaded_img.name
                else:
                    prog_img.empty()
                    st.error(f"Gagal memproses foto: {result_container_img.get('error')}")

        if st.session_state.get("hasil_foto_hd") is not None:
            st.divider()
            info = st.session_state["info_foto_hd"]
            st.success(f"🎉 **Foto berhasil ditingkatkan ke HD+!** Diproses dalam {info.get('elapsed_seconds', 0)} detik.")

            col_view1, col_view2 = st.columns(2)
            with col_view1:
                st.markdown("##### 📷 Sebelum (Asli)")
                if uploaded_img:
                    st.image(uploaded_img, use_container_width=True)
                orig_dim = info.get("original_dimensions", (0, 0))
                st.caption(f"Resolusi: **{orig_dim[0]} × {orig_dim[1]}** | {info.get('original_size_kb')} KB")
            with col_view2:
                st.markdown("##### ✨ Sesudah (HD+ AI)")
                st.image(st.session_state["hasil_foto_hd"], use_container_width=True)
                new_dim = info.get("enhanced_dimensions", (0, 0))
                st.caption(f"Resolusi: **{new_dim[0]} × {new_dim[1]}** | {info.get('enhanced_size_kb')} KB")

            out_name = f"HD_{os.path.splitext(st.session_state.get('nama_foto_asli', 'foto'))[0]}.png"
            st.download_button(
                label=f"⬇️ DOWNLOAD FOTO HD+ ({out_name})",
                data=st.session_state["hasil_foto_hd"],
                file_name=out_name,
                mime="image/png",
                type="primary",
                use_container_width=True,
                key="dl_foto_hd"
            )

    # --- TAB 2: VIDEO HD+ ---
    with tab_video:
        uploaded_vid = st.file_uploader(
            "Upload Video:",
            type=["mp4", "mkv", "mov", "avi"],
            help="Mendukung MP4, MKV, MOV, AVI",
            key="uploader_video_hd"
        )

        if uploaded_vid:
            vid_mb = round(uploaded_vid.size / (1024 * 1024), 2)
            st.success(f"✅ Video siap diproses: **{uploaded_vid.name}** ({vid_mb} MB)")
            st.progress(1.0, text=f"Status Upload: 100% Selesai ({vid_mb} MB berhasil dimuat ke browser)")
        else:
            st.info("ℹ️ **Petunjuk Upload Video**: File video (puluhan MB) membutuhkan waktu transfer upload dari laptop ke browser. Harap tunggu hingga lingkaran berputar di kotak upload selesai sebelum menekan tombol merah.")

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            scale_vid = st.selectbox(
                "Faktor Perbesaran Video:",
                options=[2, 4],
                format_func=lambda x: f"{x}x — Rekomendasi Cepat (HD)" if x == 2 else f"{x}x — Ultra HD / 4K (Lebih Lama)",
                key="scale_vid"
            )
        with col_v2:
            face_vid = st.checkbox(
                "Restorasi Wajah pada Video",
                value=False,
                help="Aktifkan deteksi & penajaman wajah di setiap frame video",
                key="face_vid"
            )

        st.write("")
        btn_enhance_vid = st.button(
            "🚀 TINGKATKAN KUALITAS VIDEO (HD+)",
            type="primary", use_container_width=True, key="btn_run_video"
        )

        if btn_enhance_vid:
            if not colab_url:
                st.error("⚠️ Harap masukkan URL Google Colab pada langkah 1!")
            elif not uploaded_vid:
                st.error("⚠️ Harap upload file video terlebih dahulu!")
            else:
                vid_mb = round(uploaded_vid.size / (1024 * 1024), 2)
                result_box_vid = {}

                def _run_vid():
                    try:
                        res_b, inf = WebController.enhance_video(
                            api_url=colab_url,
                            file=uploaded_vid,
                            scale=scale_vid,
                            face_enhance=face_vid,
                        )
                        result_box_vid["data"] = (res_b, inf)
                    except Exception as err:
                        result_box_vid["error"] = err

                th_vid = threading.Thread(target=_run_vid)
                th_vid.start()

                prog_vid = st.progress(5, text=f"📤 [Tahap 1/3] Mengirim file video ({vid_mb} MB) ke Google Colab...")
                start_vid_t = time.time()

                while th_vid.is_alive():
                    elapsed = round(time.time() - start_vid_t, 1)
                    if elapsed < 8.0:
                        pct = min(35, int(5 + (elapsed / 8.0) * 30))
                        prog_vid.progress(pct, text=f"📤 [Tahap 1/3] Mengirim video ({vid_mb} MB) ke Colab GPU... ({elapsed}s)")
                    elif elapsed < 45.0:
                        pct = min(88, int(35 + ((elapsed - 8.0) / 37.0) * 53))
                        prog_vid.progress(pct, text=f"🧠 [Tahap 2/3] GPU Colab sedang merender & upscaling frame video... ({elapsed}s)")
                    else:
                        pct = min(98, int(88 + ((elapsed - 45.0) / 30.0) * 10))
                        prog_vid.progress(pct, text=f"📥 [Tahap 3/3] Mengompresi dan mengunduh video HD+... ({elapsed}s)")
                    time.sleep(0.35)

                th_vid.join()

                if "data" in result_box_vid:
                    total_vid_time = round(time.time() - start_vid_t, 1)
                    prog_vid.progress(100, text=f"✅ Video HD+ Selesai 100%! ({total_vid_time} detik)")
                    res_vid_bytes, info_v = result_box_vid["data"]
                    st.session_state["hasil_video_hd"] = res_vid_bytes
                    st.session_state["info_video_hd"] = info_v
                    st.session_state["nama_video_asli"] = uploaded_vid.name
                else:
                    prog_vid.empty()
                    st.error(f"Gagal memproses video: {result_box_vid.get('error')}")

        if st.session_state.get("hasil_video_hd") is not None:
            st.divider()
            info_v = st.session_state["info_video_hd"]
            st.success(f"🎉 **Video berhasil ditingkatkan ke HD+!** Diproses dalam {info_v.get('elapsed_seconds', 0)} detik.")
            st.video(st.session_state["hasil_video_hd"])
            out_vid_name = f"HD_{os.path.splitext(st.session_state.get('nama_video_asli', 'video'))[0]}.mp4"
            st.download_button(
                label=f"⬇️ DOWNLOAD VIDEO HD+ ({out_vid_name})",
                data=st.session_state["hasil_video_hd"],
                file_name=out_vid_name,
                mime="video/mp4",
                type="primary",
                use_container_width=True,
                key="dl_video_hd"
            )


# --- 8. KONTEN UTAMA: REMOVE BACKGROUND ---
elif menu == "🖼️ Remove Background":
    st.title("🖼️ Remove Background")
    st.markdown(
        "Hapus latar gambar secara otomatis dengan AI lokal, pilih warna latar baru, "
        "lalu simpan sebagai PNG, JPG, ICO, WEBP, BMP, atau TIFF."
    )
    st.info("Pemrosesan dilakukan di perangkat/server aplikasi. Model AI mungkin diunduh saat pertama kali digunakan.")
    st.divider()

    uploaded_bg_image = st.file_uploader(
        "Pilih gambar:",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
        key="uploader_remove_bg",
    )

    col_bg_color, col_bg_format, col_bg_transparency = st.columns([1, 1, 1])
    with col_bg_color:
        background_color = st.color_picker(
            "Warna latar baru:",
            value="#FFFFFF",
            key="remove_bg_color",
        )
    with col_bg_format:
        output_format = st.selectbox(
            "Format simpan:",
            options=["PNG", "JPG", "ICO", "WEBP", "BMP", "TIFF"],
            key="remove_bg_format",
        )
    with col_bg_transparency:
        preserve_transparency = st.checkbox(
            "Pertahankan transparansi",
            value=False,
            help="Berlaku untuk PNG, ICO, WEBP, dan TIFF. Format JPG/BMP selalu memakai warna latar.",
            key="remove_bg_transparency",
        )

    if uploaded_bg_image:
        source_image_bytes = uploaded_bg_image.getvalue()
        source_fingerprint = hashlib.sha256(source_image_bytes).hexdigest()
        if st.session_state.get("remove_bg_source") != source_fingerprint:
            st.session_state["remove_bg_source"] = source_fingerprint
            st.session_state["remove_bg_result"] = None
            st.session_state["remove_bg_filename"] = uploaded_bg_image.name

        st.caption(f"File: **{uploaded_bg_image.name}**")
        if st.button("✂️ HAPUS BACKGROUND", type="primary", key="btn_remove_bg"):
            removal_result = {}

            def _remove_background_worker():
                try:
                    removal_result["image"] = WebController.remove_background(source_image_bytes)
                except Exception as exc:
                    removal_result["error"] = exc

            started_at = time.monotonic()
            removal_thread = threading.Thread(target=_remove_background_worker, daemon=True)
            removal_thread.start()
            progress_bar = st.progress(10, text="Menyiapkan AI untuk menghapus background...")
            progress_text = st.empty()

            while removal_thread.is_alive():
                elapsed = time.monotonic() - started_at
                progress_percent = WebController.estimate_background_removal_progress(elapsed)
                progress_bar.progress(
                    progress_percent,
                    text=f"AI menghapus background... sekitar {progress_percent}% (estimasi)",
                )
                progress_text.caption(
                    f"Pemrosesan berjalan selama {elapsed:.0f} detik. "
                    "Persentase adalah estimasi; model AI tidak menyediakan progres pasti."
                )
                time.sleep(0.25)

            removal_thread.join()
            if "error" in removal_result:
                progress_bar.empty()
                progress_text.empty()
                st.error(f"Gagal menghapus background: {removal_result['error']}")
            else:
                st.session_state["remove_bg_result"] = removal_result["image"]
                st.session_state["remove_bg_filename"] = uploaded_bg_image.name
                progress_bar.progress(100, text="Background berhasil dihapus — 100%")
                progress_text.empty()

        removed_image = st.session_state.get("remove_bg_result")
        if removed_image:
            preview_bytes = WebController.preview_background_removed_image(
                removed_image,
                background_color=background_color,
                preserve_transparency=(
                    preserve_transparency and output_format in {"PNG", "ICO", "WEBP", "TIFF"}
                ),
            )
            preview_col1, preview_col2 = st.columns(2)
            with preview_col1:
                st.markdown("##### Sebelum")
                st.image(source_image_bytes, use_container_width=True)
            with preview_col2:
                st.markdown("##### Sesudah")
                st.image(preview_bytes, use_container_width=True)

            converted_bytes, mime_type, extension = WebController.export_background_removed_image(
                removed_image,
                output_format=output_format,
                background_color=background_color,
                preserve_transparency=preserve_transparency,
            )
            base_name = os.path.splitext(
                st.session_state.get("remove_bg_filename", "gambar")
            )[0]
            st.download_button(
                label=f"⬇️ DOWNLOAD HASIL ({output_format})",
                data=converted_bytes,
                file_name=f"{base_name}_no_bg{extension}",
                mime=mime_type,
                type="primary",
                key="dl_remove_bg",
            )
    else:
        st.session_state["remove_bg_result"] = None
        st.session_state["remove_bg_source"] = None


# --- 9. KONTEN UTAMA: TOOL LAIN ---
elif menu == "🔒 Tool Lain (Segera Hadir)":
    st.title("🔒 Tool Lain")
    st.info("Fitur utilitas tambahan sedang dalam tahap pengembangan dan akan segera hadir.")
