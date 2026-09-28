"""Tkinter dashboard view."""

import tkinter as tk


class DashboardView(tk.Frame):
    """Dashboard that delegates navigation to the desktop controller."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="CUSTOM", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        tk.Label(
            self,
            text="Pilih tools yang ingin anda gunakan:",
            font=("Segoe UI", 10),
            fg="gray",
        ).pack(pady=(0, 20))

        grid_frame = tk.Frame(self)
        grid_frame.pack(pady=10)

        self._create_module_button(
            grid_frame,
            "📄  PENGGABUNG PDF\n(BY NIK)",
            "PageMergePDF",
            "#007bff",
            0,
            0,
        )
        self._create_module_button(
            grid_frame,
            "📑  PENGGABUNG PDF\n(BY ALL)",
            "PageMergeAllPDF",
            "#28a745",
            0,
            1,
        )
        self._create_module_button(
            grid_frame,
            "📝  KONVERSI PDF\nKE WORD (.DOCX)",
            "PagePdfToWord",
            "#6f42c1",
            0,
            2,
        )

    def _create_module_button(self, parent, label, frame_name, color, row, column):
        button = tk.Button(
            parent,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="white",
            width=24,
            height=4,
            relief="flat",
            cursor="hand2",
            command=lambda: self.controller.show_frame(frame_name),
        )
        button.grid(row=row, column=column, padx=12, pady=10)

