import io
import os
import threading
import time
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

from PIL import Image, ImageTk

from mvc.models import BackgroundRemoverModel


class PageBackgroundRemover(tk.Frame):
    """Tkinter view for removing image backgrounds and saving in common formats."""

    FORMAT_EXTENSIONS = {
        "PNG": ".png",
        "JPG": ".jpg",
        "ICO": ".ico",
        "WEBP": ".webp",
        "BMP": ".bmp",
        "TIFF": ".tiff",
    }

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.source_bytes = None
        self.removed_bytes = None
        self.source_name = "gambar"
        self.background_color = "#FFFFFF"
        self.preview_photo = None
        self.is_processing = False
        self._build()

    def _build(self):
        header = tk.Frame(self)
        header.pack(fill="x", padx=15, pady=12)
        ttk.Button(
            header,
            text="< Kembali",
            command=lambda: self.controller.show_frame("DashboardMenu"),
        ).pack(side="left")
        tk.Label(header, text="Remove Background", font=("Segoe UI", 12, "bold")).pack(
            side="left", padx=15
        )

        content = tk.Frame(self, padx=25, pady=10)
        content.pack(fill="both", expand=True)
        file_row = tk.Frame(content)
        file_row.pack(fill="x", pady=8)
        ttk.Button(file_row, text="Pilih Gambar...", command=self._select_image).pack(
            side="left"
        )
        self.file_label = tk.Label(file_row, text="Belum ada gambar dipilih")
        self.file_label.pack(side="left", padx=10)

        options = ttk.LabelFrame(content, text="Latar & Format Hasil", padding=10)
        options.pack(fill="x", pady=8)
        ttk.Button(options, text="Pilih Warna...", command=self._select_color).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.color_swatch = tk.Label(
            options, text=self.background_color, bg=self.background_color, width=14
        )
        self.color_swatch.grid(row=0, column=1, padx=(0, 15))
        tk.Label(options, text="Format:").grid(row=0, column=2, padx=(0, 6))
        self.format_var = tk.StringVar(value="PNG")
        self.format_box = ttk.Combobox(
            options,
            textvariable=self.format_var,
            values=list(self.FORMAT_EXTENSIONS),
            state="readonly",
            width=10,
        )
        self.format_box.grid(row=0, column=3)
        self.format_box.bind("<<ComboboxSelected>>", self._on_format_selected)
        self.transparent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options,
            text="Pertahankan transparansi (jika format mendukung)",
            variable=self.transparent_var,
            command=self._refresh_preview,
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self.preview = tk.Label(content, text="Pratinjau hasil akan tampil di sini")
        self.preview.pack(fill="both", expand=True, pady=8)
        self.progress = ttk.Progressbar(content, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 2))
        self.status = tk.Label(content, text="Pilih gambar untuk memulai.", fg="#555555")
        self.status.pack(anchor="w", pady=5)

        actions = tk.Frame(content)
        actions.pack(fill="x", pady=8)
        self.remove_button = ttk.Button(
            actions, text="Hapus Background", command=self._remove_background
        )
        self.remove_button.pack(side="left", padx=(0, 8))
        self.save_button = ttk.Button(
            actions, text="Simpan Hasil...", command=self._save_result, state="disabled"
        )
        self.save_button.pack(side="left")

    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Pilih Gambar",
            filetypes=[
                ("Gambar", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff"),
                ("Semua file", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "rb") as image_file:
                self.source_bytes = image_file.read()
        except OSError as exc:
            messagebox.showerror("Gagal membuka gambar", str(exc))
            return

        self.source_name = os.path.splitext(os.path.basename(path))[0]
        self.removed_bytes = None
        self.file_label.config(text=os.path.basename(path))
        self.preview.config(image="", text="Gambar siap diproses.")
        self.save_button.config(state="disabled")
        self.status.config(text="Gambar siap diproses.", fg="#555555")

    def _select_color(self):
        selected = colorchooser.askcolor(
            color=self.background_color, title="Pilih warna latar"
        )[1]
        if selected:
            self.background_color = selected
            self.color_swatch.config(text=selected, bg=selected)
            self._refresh_preview()

    def _on_format_selected(self, event):
        if event.widget is self.format_box:
            self._refresh_preview()

    def _remove_background(self):
        if not self.source_bytes:
            messagebox.showwarning("Peringatan", "Pilih gambar terlebih dahulu.")
            return

        image_bytes = self.source_bytes
        self.is_processing = True
        self.processing_started_at = time.monotonic()
        self.remove_button.config(state="disabled")
        self.progress["value"] = 10
        self.status.config(text="Menyiapkan AI... 10% (estimasi)", fg="#0066cc")
        self._update_progress()

        def worker():
            try:
                result = BackgroundRemoverModel.remove_background(image_bytes)
                self.after(0, lambda: self._removal_succeeded(result))
            except Exception as exc:
                self.after(0, lambda error=exc: self._removal_failed(str(error)))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress(self):
        if not self.is_processing:
            return
        elapsed = time.monotonic() - self.processing_started_at
        progress = BackgroundRemoverModel.estimate_progress(elapsed)
        self.progress["value"] = progress
        self.status.config(
            text=(
                f"AI sedang menghapus background... sekitar {progress}% (estimasi). "
                "Persentase pasti tidak tersedia dari model."
            ),
            fg="#0066cc",
        )
        self.after(250, self._update_progress)

    def _removal_succeeded(self, result):
        self.is_processing = False
        self.removed_bytes = result
        self.remove_button.config(state="normal")
        self.save_button.config(state="normal")
        self.progress["value"] = 100
        self.status.config(text="Background berhasil dihapus.", fg="#188038")
        self._refresh_preview()

    def _removal_failed(self, error):
        self.is_processing = False
        self.remove_button.config(state="normal")
        self.progress["value"] = 0
        self.status.config(text="Gagal menghapus background.", fg="#c5221f")
        messagebox.showerror("Gagal memproses gambar", error)

    def _refresh_preview(self):
        if not self.removed_bytes:
            return
        try:
            preview_bytes = BackgroundRemoverModel.preview(
                self.removed_bytes,
                background_color=self.background_color,
                preserve_transparency=(
                    self.transparent_var.get()
                    and self.format_var.get() in {"PNG", "ICO", "WEBP", "TIFF"}
                ),
            )
            with Image.open(io.BytesIO(preview_bytes)) as image:
                preview_image = image.copy()
            preview_image.thumbnail((720, 420))
            self.preview_photo = ImageTk.PhotoImage(preview_image)
            self.preview.config(image=self.preview_photo, text="")
        except Exception as exc:
            self.status.config(text=f"Gagal menampilkan pratinjau: {exc}", fg="#c5221f")

    def _save_result(self):
        if not self.removed_bytes:
            return

        output_format = self.format_var.get()
        extension = self.FORMAT_EXTENSIONS[output_format]
        output_path = filedialog.asksaveasfilename(
            title="Simpan hasil remove background",
            initialfile=f"{self.source_name}_no_bg{extension}",
            defaultextension=extension,
            filetypes=[(f"{output_format} image", f"*{extension}")],
        )
        if not output_path:
            return

        try:
            output_bytes, _, _ = BackgroundRemoverModel.export(
                self.removed_bytes,
                output_format=output_format,
                background_color=self.background_color,
                preserve_transparency=self.transparent_var.get(),
            )
            with open(output_path, "wb") as output_file:
                output_file.write(output_bytes)
        except Exception as exc:
            messagebox.showerror("Gagal menyimpan gambar", str(exc))
            return

        self.status.config(text=f"Hasil disimpan: {output_path}", fg="#188038")
        messagebox.showinfo("Sukses", f"Gambar berhasil disimpan:\n{output_path}")
