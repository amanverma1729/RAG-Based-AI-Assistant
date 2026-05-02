import customtkinter as ctk
from src.config.theme import COLORS, PDF_COLORS

class PDFSlot(ctk.CTkFrame):
    def __init__(self, parent, idx, load_callback, remove_callback):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.idx = idx
        self.color = PDF_COLORS[idx]
        self.load_callback = load_callback
        self.remove_callback = remove_callback
        
        self._build_ui()

    def _build_ui(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=7)

        # Index Badge
        badge = ctk.CTkLabel(row, text=str(self.idx+1), width=24, height=24,
            fg_color=self.color, corner_radius=7,
            font=ctk.CTkFont(size=11, weight="bold"), text_color="white")
        badge.grid(row=0, column=0, rowspan=2)

        # File Name Label
        self.name_lbl = ctk.CTkLabel(row, text=f"Slot {self.idx+1} — Empty",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"], anchor="w")
        self.name_lbl.grid(row=0, column=1, sticky="ew", padx=(8,0))

        # Status/Info Label
        self.info_lbl = ctk.CTkLabel(row, text="+ button to upload",
            font=ctk.CTkFont(size=9), text_color=COLORS["border"], anchor="w")
        self.info_lbl.grid(row=1, column=1, sticky="ew", padx=(8,0))

        row.grid_columnconfigure(1, weight=1)

        # Action Buttons
        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.grid(row=0, column=2, rowspan=2)

        ctk.CTkButton(btns, text="+", width=26, height=26,
            fg_color=self.color, hover_color=self.color,
            font=ctk.CTkFont(size=14, weight="bold"), corner_radius=6,
            command=lambda: self.load_callback(self.idx)).pack(side="left", padx=(4,2))

        ctk.CTkButton(btns, text="✕", width=26, height=26,
            fg_color=COLORS["bg_dark"], hover_color="#2D1515",
            text_color=COLORS["accent_red"], font=ctk.CTkFont(size=11),
            corner_radius=6,
            command=lambda: self.remove_callback(self.idx)).pack(side="left")

    def set_loading(self):
        self.name_lbl.configure(text="⏳ Processing...", text_color=COLORS["accent_orange"])
        self.info_lbl.configure(text="Extracting & embedding text...")

    def set_loaded(self, filename: str, pages: int, total_chunks: int, size_kb: int):
        short = filename if len(filename) <= 20 else filename[:17] + "..."
        self.name_lbl.configure(text=f"✓ {short}", text_color=self.color)
        self.info_lbl.configure(text=f"{pages} pages • {total_chunks} chunks • {size_kb}KB", text_color=COLORS["text_secondary"])
        self.configure(border_color=self.color)

    def set_error(self, msg: str):
        self.name_lbl.configure(text=f"❌ Error", text_color=COLORS["accent_red"])
        self.info_lbl.configure(text=msg[:35])

    def set_empty(self):
        self.name_lbl.configure(text=f"Slot {self.idx+1} — Empty", text_color=COLORS["text_secondary"])
        self.info_lbl.configure(text="+ button to upload", text_color=COLORS["border"])
        self.configure(border_color=COLORS["border"])
