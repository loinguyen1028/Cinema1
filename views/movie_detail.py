import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


class MovieDetail(tk.Toplevel):
    def __init__(self, parent, controller, movie_id):
        super().__init__(parent)
        self.controller = controller
        self.movie_id = movie_id

        self.title("Chi tiết phim")
        self.geometry("800x650")  # Tăng chiều cao lên một chút cho thoáng
        self.config(bg="white")
        # self.resizable(False, False) # Cho phép resize để xem nếu mô tả quá dài

        # Load dữ liệu
        self.movie = self.controller.get_detail(self.movie_id)

        if self.movie:
            self.render_ui()
        else:
            self.destroy()

    def render_ui(self):
        # 1. Header (Tên phim)
        header_frame = tk.Frame(self, bg="white", pady=20)
        header_frame.pack(fill=tk.X, padx=30)

        tk.Label(header_frame, text=self.movie.title.upper(), font=("Arial", 20, "bold"),
                 bg="white", fg="#0f1746").pack(anchor="w")

        # Đường kẻ
        tk.Frame(header_frame, bg="#ff9800", height=4, width=100).pack(anchor="w", pady=(5, 0))

        # 2. Body (Chia 2 cột: Poster - Info)
        # Sử dụng fill=tk.BOTH, expand=True để phần này chiếm không gian chính
        body_frame = tk.Frame(self, bg="white", padx=30, pady=10)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # --- CỘT TRÁI: POSTER ---
        left_col = tk.Frame(body_frame, bg="white", width=250)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30), anchor="n")

        self.poster_lbl = tk.Label(left_col, bg="#f0f0f0", text="No Poster")
        self.poster_lbl.pack()

        if self.movie.poster_path and os.path.exists(self.movie.poster_path):
            try:
                img = Image.open(self.movie.poster_path)
                img = img.resize((220, 330), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.poster_lbl.config(image=photo, text="")
                self.poster_lbl.image = photo
            except:
                pass
        else:
            tk.Frame(self.poster_lbl, bg="#ddd", width=220, height=330).pack()

        # --- CỘT PHẢI: THÔNG TIN CHI TIẾT ---
        right_col = tk.Frame(body_frame, bg="white")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor="n")

        def add_info_row(label, value, is_multiline=False):
            row = tk.Frame(right_col, bg="white", pady=5)
            row.pack(fill=tk.X)

            tk.Label(row, text=label, font=("Arial", 10, "bold"), bg="white", fg="#555", width=15, anchor="w").pack(
                side=tk.LEFT, anchor="n")

            if is_multiline:
                lbl = tk.Label(row, text=value, font=("Arial", 11), bg="white", fg="#333",
                               justify=tk.LEFT, wraplength=400, anchor="w")
                lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                tk.Label(row, text=value, font=("Arial", 11), bg="white", fg="#333", anchor="w").pack(side=tk.LEFT,
                                                                                                      fill=tk.X,
                                                                                                      expand=True)

        extra = self.movie.extra_info if self.movie.extra_info else {}

        add_info_row("Thời lượng:", f"{self.movie.duration_min} phút")
        add_info_row("Quốc gia:", extra.get("country", "N/A"))
        add_info_row("Thể loại:", extra.get("genre", "N/A"), is_multiline=True)
        add_info_row("Giới hạn tuổi:", extra.get("age_limit", "N/A"))
        add_info_row("Hình thức:", extra.get("language", "N/A"))
        add_info_row("Diễn viên:", extra.get("actors", "N/A"), is_multiline=True)

        # 3. Footer Section (Mô tả + Nút Đóng)
        footer_section = tk.Frame(self, bg="white")
        footer_section.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=(0, 20))

        btn_frame = tk.Frame(footer_section, bg="white")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        tk.Button(btn_frame, text="Đóng", bg="#555", fg="white", font=("Arial", 10, "bold"),
                  width=10, relief="flat", command=self.destroy, cursor="hand2").pack(side=tk.RIGHT)

        desc_frame = tk.LabelFrame(footer_section, text="Nội dung phim", bg="white", font=("Arial", 11, "bold"),
                                   fg="#333", padx=15, pady=15)
        desc_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        desc_text = self.movie.description if self.movie.description else "Chưa có mô tả."

        # --- THÊM SCROLLBAR ---
        scrollbar = tk.Scrollbar(desc_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        txt_desc = tk.Text(desc_frame, font=("Arial", 11), bg="white", relief="flat", wrap=tk.WORD, height=8,
                           yscrollcommand=scrollbar.set)
        txt_desc.insert("1.0", desc_text)
        txt_desc.config(state=tk.DISABLED)  # Read-only
        txt_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=txt_desc.yview)