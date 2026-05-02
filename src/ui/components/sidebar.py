import customtkinter as ctk
from src.config.theme import COLORS
from src.config.settings import MAX_PDFS
from src.ui.components.pdf_slot import PDFSlot

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, callbacks):
        super().__init__(parent, width=310, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.callbacks = callbacks # Dict containing 'load_pdf', 'remove_pdf', 'clear_all', 'recheck_ollama'
        self.slot_widgets = []
        
        self.grid_propagate(False)
        self.grid_rowconfigure(3, weight=1)
        self._build_ui()

    def _build_ui(self):
        # Logo Frame
        logo_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=80)
        logo_frame.grid(row=0, column=0, sticky="ew")
        logo_frame.grid_propagate(False)

        ctk.CTkLabel(logo_frame, text="📄", font=ctk.CTkFont(size=28)).place(x=16, y=14)
        ctk.CTkLabel(logo_frame, text="PDF Intelligence",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"]).place(x=58, y=12)
        ctk.CTkLabel(logo_frame, text="100% OFFLINE • No API Key",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["accent_green"]).place(x=58, y=36)

        self.ollama_badge = ctk.CTkLabel(logo_frame, text="🔄 Checking Ollama...",
            font=ctk.CTkFont(size=10), text_color=COLORS["text_secondary"])
        self.ollama_badge.place(x=58, y=55)

        # Status Info Bar
        info = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        info.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 6))

        self.status_bar = ctk.CTkLabel(info,
            text="🔄 Loading AI model...",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["accent_orange"],
            wraplength=260, justify="left")
        self.status_bar.pack(padx=12, pady=8)

        # Header for PDFs
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 2))
        ctk.CTkLabel(hdr, text="📁 Load PDFs", font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(hdr, text=f"max {MAX_PDFS}", font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]).pack(side="left", padx=6)

        # Scrollable Slots
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"])
        scroll.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 6))

        for i in range(MAX_PDFS):
            w = PDFSlot(scroll, i, self.callbacks['load_pdf'], self.callbacks['remove_pdf'])
            w.pack(fill="x", pady=3)
            self.slot_widgets.append(w)

        # Bottom Actions
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.grid(row=4, column=0, sticky="sew", padx=12, pady=8)

        self.count_lbl = ctk.CTkLabel(bot, text="0 / 5 PDFs loaded",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"])
        self.count_lbl.pack(pady=(0,5))

        ctk.CTkButton(bot, text="🗑  Clear All", height=34, corner_radius=8,
            fg_color=COLORS["bg_card"], hover_color="#2A1515",
            text_color=COLORS["accent_red"], font=ctk.CTkFont(size=12),
            command=self.callbacks['clear_all']).pack(fill="x", pady=(0,4))

        ctk.CTkButton(bot, text="🦙  Recheck Ollama", height=34, corner_radius=8,
            fg_color=COLORS["bg_card"], hover_color="#1A1535",
            text_color=COLORS["accent_purple"], font=ctk.CTkFont(size=12),
            command=self.callbacks['recheck_ollama']).pack(fill="x")

    def update_status(self, msg: str, color_key: str):
        color_map = {
            "green": COLORS["accent_green"], "red": COLORS["accent_red"],
            "orange": COLORS["accent_orange"], "purple": COLORS["accent_purple"],
            "cyan": COLORS["accent_cyan"]
        }
        c = color_map.get(color_key, COLORS["text_secondary"])
        self.status_bar.configure(text=msg, text_color=c)

    def update_ollama_badge(self, name: str, is_active: bool):
        if is_active:
            self.ollama_badge.configure(text=f"🦙 Ollama: {name}", text_color=COLORS["accent_purple"])
        else:
            self.ollama_badge.configure(text="🔌 Ollama: Not found (optional)", text_color=COLORS["text_secondary"])

    def update_pdf_count(self, count: int):
        self.count_lbl.configure(
            text=f"{count} / {MAX_PDFS} PDFs loaded",
            text_color=COLORS["accent_green"] if count > 0 else COLORS["text_secondary"])

    def get_slot(self, idx: int) -> PDFSlot:
        return self.slot_widgets[idx]
