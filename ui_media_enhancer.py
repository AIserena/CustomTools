import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from mvc.models.media_enhancer_model import MediaEnhancerModel


class PageMediaEnhancer(tk.Frame):
    """Tkinter view for HD+ Video & Photo enhancement integrated with Google Colab."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_file = None
        self.is_processing = False
        self.setup_ui()

    def setup_ui(self):
        # 1. Header + Tombol Kembali
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=15, pady=12)

        btn_back = ttk.Button(
            header_frame,
            text="< Kembali",
            command=lambda: self.controller.show_frame("DashboardMenu"),
        )
        btn_back.pack(side="left")

        lbl_title = tk.Label(
            header_frame,
            text="HD+ Video & Foto (AI Colab)",
            font=("Segoe UI", 12, "bold"),
        )
        lbl_title.pack(side="left", padx=15)

        lbl_badge = tk.Label(
            header_frame,
            text="GPU Super Resolution",
            font=("Segoe UI", 9, "bold"),
            bg="#fce8e6",
            fg="#c5221f",
            padx=8,
            pady=2,
        )
        lbl_badge.pack(side="left")

        # 2. Main Container
        container = tk.Frame(self, padx=25, pady=5)
        container.pack(fill="both", expand=True)

        # Connection Bar (Colab API URL)
        conn_frame = ttk.LabelFrame(container, text="1. Pengaturan Koneksi API Google Colab", padding=10)
        conn_frame.pack(fill="x", pady=(0, 10))

        tk.Label(conn_frame, text="URL Google Colab:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.entry_url = ttk.Entry(conn_frame)
        self.entry_url.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.entry_url.insert(0, "https://xxxx.trycloudflare.com")
        conn_frame.columnconfigure(1, weight=1)

        btn_ping = ttk.Button(conn_frame, text="🔌 Tes Koneksi", command=self.tes_koneksi)
        btn_ping.grid(row=0, column=2, padx=(0, 8))

        self.lbl_conn_status = tk.Label(conn_frame, text="⚪ Belum tersambung", font=("Segoe UI", 8, "italic"), fg="gray")
        self.lbl_conn_status.grid(row=1, column=1, sticky="w", pady=(4, 0))

        # Media Selection & Settings
        media_frame = ttk.LabelFrame(container, text="2. Pilih File Media & Opsi HD+", padding=10)
        media_frame.pack(fill="x", pady=(0, 10))
        media_frame.columnconfigure(1, weight=1)

        # Mode Radio
        self.var_mode = tk.StringVar(value="image")
        tk.Label(media_frame, text="Tipe Media:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4, padx=(0, 8))
        mode_radio_frame = tk.Frame(media_frame)
        mode_radio_frame.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Radiobutton(mode_radio_frame, text="📸 Foto / Gambar", value="image", variable=self.var_mode).pack(side="left", padx=(0, 15))
        ttk.Radiobutton(mode_radio_frame, text="🎥 Video", value="video", variable=self.var_mode).pack(side="left")

        # File Chooser
        tk.Label(media_frame, text="File Input:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4, padx=(0, 8))
        self.entry_file = ttk.Entry(media_frame)
        self.entry_file.grid(row=1, column=1, sticky="ew", pady=4, padx=(0, 8))
        btn_choose = ttk.Button(media_frame, text="Cari File...", command=self.pilih_file)
        btn_choose.grid(row=1, column=2, pady=4)

        # Scale Factor
        tk.Label(media_frame, text="Faktor Perbesaran:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4, padx=(0, 8))
        self.combo_scale = ttk.Combobox(media_frame, values=["2x (HD)", "4x (Ultra HD/4K)"], state="readonly", width=18)
        self.combo_scale.current(1)
        self.combo_scale.grid(row=2, column=1, sticky="w", pady=4)

        # Face Enhance Checkbox
        self.var_face = tk.BooleanVar(value=True)
        self.chk_face = ttk.Checkbutton(media_frame, text="Restorasi & Penajaman Detail Wajah (Face Restoration)", variable=self.var_face)
        self.chk_face.grid(row=3, column=1, sticky="w", pady=4)

        # Folder Tujuan
        tk.Label(media_frame, text="Folder Simpan:", font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w", pady=4, padx=(0, 8))
        self.entry_dest = ttk.Entry(media_frame)
        self.entry_dest.grid(row=4, column=1, sticky="ew", pady=4, padx=(0, 8))
        btn_dest = ttk.Button(media_frame, text="Pilih Folder...", command=self.pilih_folder_tujuan)
        btn_dest.grid(row=4, column=2, pady=4)

        # Progress & Status
        self.progress_bar = ttk.Progressbar(container, orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(5, 4))

        self.lbl_status = tk.Label(container, text="Siap memproses. Pastikan server Colab aktif.", font=("Segoe UI", 9), fg="#555555")
        self.lbl_status.pack(anchor="w", pady=(0, 8))

        # Action Buttons
        btn_action_frame = tk.Frame(container)
        btn_action_frame.pack(fill="x", pady=(4, 10))

        self.btn_proses = tk.Button(
            btn_action_frame,
            text="🚀 MULAI ENHANCE HD+",
            bg="#d93025",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.mulai_proses,
        )
        self.btn_proses.pack(side="left", padx=(0, 10))

        self.btn_buka_folder = tk.Button(
            btn_action_frame,
            text="📂 BUKA FOLDER HASIL",
            bg="#007bff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self.buka_folder_hasil,
        )

    def tes_koneksi(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Harap masukkan URL API Google Colab terlebih dahulu!")
            return

        self.lbl_conn_status.config(text="⏳ Memeriksa koneksi ke Colab...", fg="#0066cc")
        self.update_idletasks()

        def _ping_worker():
            res = MediaEnhancerModel.ping_colab(url, timeout=5)
            if res["connected"]:
                details = res.get("details", {})
                gpu = details.get("gpu", "GPU Aktif")
                self.after(0, lambda: self.lbl_conn_status.config(text=f"🟢 Terhubung! ({gpu})", fg="#28a745"))
            else:
                self.after(0, lambda: self.lbl_conn_status.config(text=f"🔴 Gagal terhubung: {res.get('message', '')[:40]}", fg="#dc3545"))

        threading.Thread(target=_ping_worker, daemon=True).start()

    def pilih_file(self):
        mode = self.var_mode.get()
        if mode == "image":
            file_types = [("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        else:
            file_types = [("Video Files", "*.mp4;*.mkv;*.mov;*.avi")]

        file_path = filedialog.askopenfilename(title="Pilih File Media", filetypes=file_types)
        if file_path:
            self.selected_file = file_path
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, file_path)

            if not self.entry_dest.get():
                folder = os.path.dirname(file_path)
                self.entry_dest.delete(0, tk.END)
                self.entry_dest.insert(0, os.path.join(folder, "HASIL_HD"))

    def pilih_folder_tujuan(self):
        folder = filedialog.askdirectory(title="Pilih Folder Hasil")
        if folder:
            self.entry_dest.delete(0, tk.END)
            self.entry_dest.insert(0, folder)

    def buka_folder_hasil(self):
        folder = self.entry_dest.get().strip()
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showinfo("Info", "Folder belum dibuat atau belum ada file.")

    def mulai_proses(self):
        if self.is_processing:
            return

        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Harap isi URL Google Colab!")
            return

        file_path = self.entry_file.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Peringatan", "File media input tidak ditemukan!")
            return

        dest_folder = self.entry_dest.get().strip()
        if not dest_folder:
            messagebox.showwarning("Peringatan", "Harap tentukan folder penyimpanan hasil!")
            return

        scale = 4 if "4x" in self.combo_scale.get() else 2
        face = self.var_face.get()
        mode = self.var_mode.get()

        self.is_processing = True
        self.btn_proses.config(state="disabled", text="⏳ Sedang Memproses di GPU Colab...")
        self.btn_buka_folder.pack_forget()
        self.progress_bar.start(10)
        self.lbl_status.config(text="Mengirim file ke Google Colab dan menjalankan pemrosesan AI...", fg="#0066cc")

        thread = threading.Thread(
            target=self._proses_worker,
            args=(url, file_path, dest_folder, mode, scale, face),
            daemon=True,
        )
        thread.start()

    def _proses_worker(self, url, file_path, dest_folder, mode, scale, face):
        os.makedirs(dest_folder, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()

            if mode == "image":
                out_name = f"{base_name}_HD_{scale}x.png"
                out_path = os.path.join(dest_folder, out_name)
                res_bytes, info = MediaEnhancerModel.enhance_image(
                    api_url=url,
                    image_bytes=raw_bytes,
                    filename=os.path.basename(file_path),
                    scale=scale,
                    face_enhance=face,
                )
            else:
                out_name = f"{base_name}_HD_{scale}x.mp4"
                out_path = os.path.join(dest_folder, out_name)
                res_bytes, info = MediaEnhancerModel.enhance_video(
                    api_url=url,
                    video_bytes=raw_bytes,
                    filename=os.path.basename(file_path),
                    scale=scale,
                    face_enhance=face,
                )

            with open(out_path, "wb") as f:
                f.write(res_bytes)

            self.after(0, lambda: self._selesai_sukses(out_path, info))
        except Exception as exc:
            self.after(0, lambda: self._selesai_gagal(str(exc)))

    def _selesai_sukses(self, out_path, info):
        self.is_processing = False
        self.progress_bar.stop()
        self.btn_proses.config(state="normal", text="🚀 MULAI ENHANCE HD+")
        self.btn_buka_folder.pack(side="left")
        elapsed = info.get("elapsed_seconds", 0)
        self.lbl_status.config(
            text=f"✅ Selesai dalam {elapsed} detik! Disimpan ke: {os.path.basename(out_path)}",
            fg="#28a745",
        )
        messagebox.showinfo("Sukses", f"Media berhasil ditingkatkan kualitasnya ke HD+!\nDisimpan di:\n{out_path}")

    def _selesai_gagal(self, error_msg):
        self.is_processing = False
        self.progress_bar.stop()
        self.btn_proses.config(state="normal", text="🚀 MULAI ENHANCE HD+")
        self.lbl_status.config(text=f"❌ Gagal: {error_msg[:60]}", fg="#dc3545")
        messagebox.showerror("Gagal", f"Proses peningkatan HD+ gagal:\n{error_msg}")
