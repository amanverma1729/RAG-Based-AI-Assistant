import time
import re
import customtkinter as ctk
from src.config.theme import COLORS

class ChatArea(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_blue"]
        )
        self.grid_columnconfigure(0, weight=1)
        self.is_thinking = False

    def add_message(self, text: str, sender: str) -> str:
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=8, pady=5)
        bid = f"b{int(time.time()*1000)}"
        f._bid = bid

        clean = self._clean(text)

        if sender == "user":
            out = ctk.CTkFrame(f, fg_color="transparent")
            out.pack(anchor="e")
            ctk.CTkLabel(out, text="👤 You", font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS["accent_blue"]).pack(anchor="e", padx=4)
            bub = ctk.CTkFrame(out, fg_color=COLORS["user_bubble"], corner_radius=14)
            bub.pack(anchor="e")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=13),
                text_color=COLORS["text_primary"],
                wraplength=580, justify="left", padx=14, pady=9).pack()

        elif sender == "ai":
            out = ctk.CTkFrame(f, fg_color="transparent")
            out.pack(anchor="w", fill="x")
            ctk.CTkLabel(out, text="🤖 PDF AI (Offline)",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=COLORS["accent_purple"]).pack(anchor="w", padx=4)
            bub = ctk.CTkFrame(out, fg_color=COLORS["ai_bubble"],
                corner_radius=14, border_width=1, border_color=COLORS["border"])
            bub.pack(anchor="w", fill="x")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=13),
                text_color=COLORS["text_primary"],
                wraplength=760, justify="left",
                padx=14, pady=11, anchor="w").pack(fill="x")

        elif sender == "system":
            bub = ctk.CTkFrame(f, fg_color=COLORS["bg_card"],
                corner_radius=10, border_width=1, border_color=COLORS["border"])
            bub.pack(fill="x")
            ctk.CTkLabel(bub, text=clean, font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"],
                wraplength=820, justify="left",
                padx=14, pady=9, anchor="w").pack(fill="x")

        self.scroll_bottom()
        return bid

    def show_thinking(self) -> str:
        self.is_thinking = True
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=8, pady=5)
        bid = f"thinking_{int(time.time()*1000)}"
        f._bid = bid
        self._thinking_frame = f

        out = ctk.CTkFrame(f, fg_color="transparent")
        out.pack(anchor="w")
        ctk.CTkLabel(out, text="🤖 PDF AI (Offline)",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["accent_purple"]).pack(anchor="w", padx=4)
        bub = ctk.CTkFrame(out, fg_color=COLORS["thinking"],
            corner_radius=14, border_width=1, border_color=COLORS["accent_purple"])
        bub.pack(anchor="w")
        self._t_lbl = ctk.CTkLabel(bub, text="🔍 Extracting relevant content...",
            font=ctk.CTkFont(size=13), text_color=COLORS["accent_purple"],
            padx=14, pady=10)
        self._t_lbl.pack()
        self._animate_thinking()
        self.scroll_bottom()
        return bid

    def remove_thinking(self):
        self.is_thinking = False
        try:
            self._thinking_frame.destroy()
        except:
            pass

    def _animate_thinking(self):
        if not self.is_thinking:
            return
        frames = [
            "🔍 Searching PDFs...",
            "🧠 Comparing embeddings...",
            "📊 Extracting relevant chunks...",
            "✍️  Generating answer...",
        ]
        n = getattr(self, "_tf", 0)
        try:
            self._t_lbl.configure(text=frames[n % len(frames)])
        except:
            return
        self._tf = n + 1
        self.after(600, self._animate_thinking)

    def scroll_bottom(self):
        self.after(120, lambda: self._parent_canvas.yview_moveto(1.0))

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _clean(self, text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*",     r"\1", text)
        text = re.sub(r"`([^`]+)`",     r"[\1]", text)
        return text
