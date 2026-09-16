import os
import sys
import tkinter as tk
from tkinter import ttk
from ui_merge_pdf import PageMergePDF
from ui_merge_all import PageMergeAllPDF

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DashboardMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- TAMPILKAN LOGO DI DASHBOARD ---
        logo_png_path = resource_path("sgi_logo.png")
        if os.path.exists(logo_png_path):
            # 1. Load gambar asli
            gambar_ori = tk.PhotoImage(file=logo_png_path)
            
            # 2. ATUR UKURAN DI SINI (Ubah angka 3 sesuai kebutuhan)
            # subsample(2, 2) = diperkecil 2x (setengahnya)
            # subsample(3, 3) = diperkecil 3x
            # subsample(4, 4) = diperkecil 4x
            self.img_logo = gambar_ori.subsample(5, 5) 
            
            # 3. Tampilkan gambar
            lbl_logo_img = tk.Label(self, image=self.img_logo)
            lbl_logo_img.pack(pady=(30, 0))

        # Judul Dashboard
        lbl_title = tk.Label(self, text="", font=("Segoe UI", 16, "bold"))
        lbl_title.pack(pady=(10, 5))

        lbl_subtitle = tk.Label(self, text="Pilih tools yang ingin anda gunakan:", font=("Segoe UI", 10), fg="gray")
        lbl_subtitle.pack(pady=(0, 20))

        # Grid Tempat Tombol Tools
        grid_frame = tk.Frame(self)
        grid_frame.pack(pady=10)

        # 1. Tombol Tool 1: Merge PDF (Aktif)
        btn_merge = tk.Button(
            grid_frame,
            text="📄  PENGGABUNG PDF\n(BY NIK)",
            font=("Segoe UI", 10, "bold"),
            bg="#007bff", fg="white",
            width=24, height=4,
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame("PageMergePDF")
        )
        btn_merge.grid(row=0, column=0, padx=15, pady=10)

        # 2. Tombol Tool 2: Merge PDF (By All) (Aktif)
        btn_tool2 = tk.Button(
            grid_frame,
            text="📑  PENGGABUNG PDF\n(BY ALL)",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745", fg="white",
            width=24, height=4,
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame("PageMergeAllPDF")
        )
        btn_tool2.grid(row=0, column=1, padx=15, pady=10)


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tools SGI - Multi Utility Desktop")

        self.state('zoomed')
        self.resizable(True, True)
        self.minsize(650, 480)

        # Icon Title Bar (TETAP PAKAI .ICO)
        logo_ico_path = resource_path("sgi_logo.ico")
        if os.path.exists(logo_ico_path):
            try:
                self.iconbitmap(logo_ico_path)
            except Exception:
                pass

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (DashboardMenu, PageMergePDF, PageMergeAllPDF):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()