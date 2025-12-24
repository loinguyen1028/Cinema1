import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os




class theme:
    PRIMARY = "#5c6bc0"
    PRIMARY_DARK = "#3949ab"
    BG_MAIN = "#f0f2f5"
    BG_CARD = "#ffffff"
    TEXT_MAIN = "#333333"
    TEXT_SUB = "#666666"
    TEXT_LIGHT = "#ffffff"
    BORDER = "#e0e0e0"


class MovieDetail(tk.Toplevel):
    def __init__(self, parent, controller, movie_id):
        super().__init__(parent)
        self.controller = controller
        self.movie_id = movie_id

        self.title("Chi tiết phim")
        self.geometry("800x650")
        self.config(bg=theme.BG_MAIN)
        self.grab_set()

        # Load dữ liệu
        self.movie = self.controller.get_detail(self.movie_id)
        if not self.movie:
            self.destroy()
            return

        self.render_ui()

    def render_ui(self):
        # ================= HEADER =================
        header_frame = tk.Frame(self, bg=theme.BG_CARD, pady=20)
        header_frame.pack(fill=tk.X, padx=30, pady=(30, 10))

        tk.Label(
            header_frame,
            text=self.movie.title.upper(),
            font=("Arial", 20, "bold"),
            bg=theme.BG_CARD,
            fg=theme.PRIMARY_DARK
        ).pack(anchor="w")

        tk.Frame(
            header_frame,
            bg=theme.PRIMARY,
            height=4,
            width=120
        ).pack(anchor="w", pady=(6, 0))

        # ================= BODY =================
        body_frame = tk.Frame(
            self,
            bg=theme.BG_CARD,
            padx=30,
            pady=20,
            highlightbackground=theme.BORDER,
            highlightthickness=1
        )
        body_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        # -------- LEFT: POSTER --------
        left_col = tk.Frame(body_frame, bg=theme.BG_CARD, width=240)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30), anchor="n")

        poster_holder = tk.Frame(
            left_col,
            bg="#eeeeee",
            width=220,
            height=330
        )
        poster_holder.pack()
        poster_holder.pack_propagate(False)

        self.poster_lbl = tk.Label(poster_holder, bg="#eeeeee", text="NO POSTER")
        self.poster_lbl.pack(fill=tk.BOTH, expand=True)

        if self.movie.poster_path and os.path.exists(self.movie.poster_path):
            try:
                img = Image.open(self.movie.poster_path)
                img = img.resize((220, 330), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.poster_lbl.config(image=photo, text="")
                self.poster_lbl.image = photo
            except:
                pass

        # -------- RIGHT: INFO --------
        right_col = tk.Frame(body_frame, bg=theme.BG_CARD)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def add_info_row(label, value, multiline=False):
            row = tk.Frame(right_col, bg=theme.BG_CARD, pady=6)
            row.pack(fill=tk.X)

            tk.Label(
                row,
                text=label,
                font=("Arial", 10, "bold"),
                bg=theme.BG_CARD,
                fg=theme.TEXT_SUB,
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT, anchor="n")

            if multiline:
                tk.Label(
                    row,
                    text=value,
                    font=("Arial", 11),
                    bg=theme.BG_CARD,
                    fg=theme.TEXT_MAIN,
                    justify=tk.LEFT,
                    wraplength=420,
                    anchor="w"
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                tk.Label(
                    row,
                    text=value,
                    font=("Arial", 11),
                    bg=theme.BG_CARD,
                    fg=theme.TEXT_MAIN,
                    anchor="w"
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        extra = self.movie.extra_info if self.movie.extra_info else {}

        add_info_row("Thời lượng:", f"{self.movie.duration_min} phút")
        add_info_row("Quốc gia:", extra.get("country", "N/A"))
        add_info_row("Thể loại:", extra.get("genre", "N/A"), multiline=True)
        add_info_row("Giới hạn tuổi:", extra.get("age_limit", "N/A"))
        add_info_row("Ngôn ngữ:", extra.get("language", "N/A"))
        add_info_row("Diễn viên:", extra.get("actors", "N/A"), multiline=True)

        # ================= FOOTER =================
        footer = tk.Frame(self, bg=theme.BG_MAIN)
        footer.pack(fill=tk.BOTH, expand=False, padx=30, pady=(10, 30))

        desc_frame = tk.LabelFrame(
            footer,
            text="Nội dung phim",
            bg=theme.BG_CARD,
            fg=theme.TEXT_MAIN,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        )
        desc_frame.pack(fill=tk.BOTH, expand=True)

        desc_text = self.movie.description or "Chưa có mô tả."

        scrollbar = tk.Scrollbar(desc_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        txt_desc = tk.Text(
            desc_frame,
            font=("Arial", 11),
            bg=theme.BG_CARD,
            relief="flat",
            wrap=tk.WORD,
            height=8,
            yscrollcommand=scrollbar.set
        )
        txt_desc.insert("1.0", desc_text)
        txt_desc.config(state=tk.DISABLED)
        txt_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=txt_desc.yview)

        # -------- BUTTON --------
        btn_frame = tk.Frame(footer, bg=theme.BG_MAIN)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        tk.Button(
            btn_frame,
            text="Đóng",
            bg=theme.PRIMARY,
            fg=theme.TEXT_LIGHT,
            activebackground=theme.PRIMARY_DARK,
            font=("Arial", 10, "bold"),
            width=12,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        ).pack(side=tk.RIGHT)
