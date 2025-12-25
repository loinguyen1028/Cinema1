import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk

try:
    from utils.omdb_helper import fetch_movie_info
except ImportError:
    def fetch_movie_info(name):
        return None


class MovieDialog(tk.Toplevel):
    POSTER_EMPTY_SIZE = (120, 160)
    POSTER_FULL_SIZE = (180, 240)

    def __init__(self, parent, controller, mode="add", movie_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.movie_id = movie_id
        self.on_success = on_success

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "input": "#020617",
            "btn": "#2563eb",
            "danger": "#dc2626"
        }

        self.title("Thêm phim mới" if mode == "add" else "Chỉnh sửa phim")
        self.geometry("950x720")
        self.config(bg=self.colors["bg"])
        self.grab_set()

        self.poster_img = None
        self.current_poster_path = ""
        self.movie_data = self.load_initial_data()
        self.render_ui()

    # =====================================================
    def load_initial_data(self):
        data = {
            "name": "", "genre": "", "actors": "", "lang": "Lồng tiếng",
            "age": "16", "duration": "", "country": "Mỹ", "desc": ""
        }
        if self.mode == "edit" and self.movie_id:
            movie = self.controller.get_detail(self.movie_id)
            if movie:
                data["name"] = movie.title
                data["duration"] = str(movie.duration_min)
                data["desc"] = movie.description or ""
                self.current_poster_path = movie.poster_path or ""

                extra = movie.extra_info or {}
                data["genre"] = extra.get("genre", "")
                data["country"] = extra.get("country", "Mỹ")
                data["actors"] = extra.get("actors", "")
                data["lang"] = extra.get("language", "Lồng tiếng")
                data["age"] = extra.get("age_limit", "16")
        return data

    # =====================================================
    def render_ui(self):
        container = tk.Frame(self, bg=self.colors["bg"], padx=30, pady=25)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text=self.title(),
            font=("Arial", 17, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        ).pack(anchor="w", pady=(0, 20))

        # ROW 1
        row1 = tk.Frame(container, bg=self.colors["bg"])
        row1.pack(fill=tk.X)

        self.e_name = self.create_input(row1, "Tên phim", self.movie_data["name"], expand=True)

        tk.Button(
            row1, text="⚡ AUTO",
            bg=self.colors["primary"], fg="#111827",
            font=("Arial", 9, "bold"),
            relief="flat", padx=12,
            command=self.auto_fill_data
        ).pack(side=tk.LEFT, padx=10, pady=18)

        self.lb_genre = self.create_genre_box(row1)

        # ROW 2
        row2 = tk.Frame(container, bg=self.colors["bg"])
        row2.pack(fill=tk.X, pady=10)

        self.e_actors = self.create_input(row2, "Diễn viên", self.movie_data["actors"], expand=True)
        self.e_duration = self.create_input(row2, "Thời lượng (phút)", self.movie_data["duration"], width=15)
        self.cbo_country = self.create_combo(row2, "Quốc gia", self.movie_data["country"],
                                             ["Việt Nam", "Mỹ", "Hàn Quốc", "Thái Lan"], width=18)

        # ROW 3
        row3 = tk.Frame(container, bg=self.colors["bg"])
        row3.pack(fill=tk.X, pady=10)

        self.cbo_lang = self.create_combo(row3, "Hình thức",
                                          self.movie_data["lang"],
                                          ["Lồng tiếng", "Phụ đề", "Thuyết minh"], expand=True)

        self.cbo_age = self.create_combo(row3, "Giới hạn tuổi", self.movie_data["age"],
                                         ["P", "13", "16", "18"], width=15)

        # ROW 4
        row4 = tk.Frame(container, bg=self.colors["bg"])
        row4.pack(fill=tk.BOTH, expand=True, pady=10)

        self.txt_desc = self.create_textarea(row4, "Mô tả", self.movie_data["desc"])
        self.create_poster_panel(row4)

    # =====================================================
    def create_input(self, parent, label, value, expand=False, width=None):
        f = tk.Frame(parent, bg=self.colors["bg"])
        f.pack(side=tk.LEFT, fill=tk.X, expand=expand, padx=5)
        tk.Label(f, text=label, fg=self.colors["muted"], bg=self.colors["bg"], font=("Arial", 9)).pack(anchor="w")
        e = tk.Entry(f, font=("Arial", 11), bg=self.colors["input"], fg=self.colors["text"],
                     insertbackground="white", relief="flat", width=width)
        e.insert(0, value)
        e.pack(fill=tk.X, ipady=6, pady=4)
        return e

    def create_combo(self, parent, label, value, values, expand=False, width=None):
        f = tk.Frame(parent, bg=self.colors["bg"])
        f.pack(side=tk.LEFT, fill=tk.X, expand=expand, padx=5)
        tk.Label(f, text=label, fg=self.colors["muted"], bg=self.colors["bg"], font=("Arial", 9)).pack(anchor="w")
        c = ttk.Combobox(f, values=values, font=("Arial", 11), width=width, state="readonly")
        c.set(value)
        c.pack(fill=tk.X, pady=4)
        return c

    def create_textarea(self, parent, label, value):
        f = tk.Frame(parent, bg=self.colors["bg"])
        f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(f, text=label, fg=self.colors["muted"], bg=self.colors["bg"], font=("Arial", 9)).pack(anchor="w")
        txt = tk.Text(f, font=("Arial", 11), bg=self.colors["input"],
                      fg=self.colors["text"], insertbackground="white", height=8, relief="flat")
        txt.insert("1.0", value)
        txt.pack(fill=tk.BOTH, expand=True, pady=4)
        return txt

    def create_genre_box(self, parent):
        f = tk.Frame(parent, bg=self.colors["bg"], width=220)
        f.pack(side=tk.RIGHT, padx=10)
        tk.Label(f, text="Thể loại", fg=self.colors["muted"], bg=self.colors["bg"], font=("Arial", 9)).pack(anchor="w")
        lb = tk.Listbox(f, selectmode=tk.MULTIPLE, height=5,
                        bg=self.colors["input"], fg=self.colors["text"],
                        selectbackground=self.colors["btn"], relief="flat")
        genres = ["Hành động", "Kinh dị", "Tình cảm", "Hài", "Hoạt hình", "Viễn tưởng", "Tâm lý", "Gia đình"]
        for g in genres:
            lb.insert(tk.END, g)
            if g in self.movie_data["genre"]:
                lb.selection_set(tk.END)
        lb.pack(fill=tk.X)
        return lb

    # =====================================================
    def create_poster_panel(self, parent):
        right = tk.Frame(parent, bg=self.colors["bg"], width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=15)

        self.poster_border = tk.Frame(right, bg=self.colors["primary"], padx=2, pady=2)
        self.poster_border.pack(pady=10)

        self.lbl_poster = tk.Label(
            self.poster_border,
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Arial", 10, "bold"),
            text="NO POSTER",
            width=15,
            height=9
        )
        self.lbl_poster.pack()

        tk.Button(
            right, text="📂 Chọn ảnh",
            bg=self.colors["btn"], fg="white",
            relief="flat", command=self.choose_image
        ).pack(pady=5)

        tk.Button(
            right, text="💾 LƯU",
            bg=self.colors["primary"], fg="#111827",
            font=("Arial", 11, "bold"),
            relief="flat", command=self.save_action
        ).pack(side=tk.BOTTOM, pady=10)

        if self.current_poster_path:
            self.load_image_to_label(self.current_poster_path)

    # =====================================================
    def load_image_to_label(self, path):
        if not os.path.exists(path):
            return

        img = Image.open(path).resize(self.POSTER_FULL_SIZE, Image.Resampling.LANCZOS)
        self.poster_img = ImageTk.PhotoImage(img)

        self.lbl_poster.config(
            image=self.poster_img,
            text="",
            width=self.POSTER_FULL_SIZE[0],
            height=self.POSTER_FULL_SIZE[1]
        )

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png")])
        if path:
            self.current_poster_path = path
            self.load_image_to_label(path)

    # =====================================================
    def auto_fill_data(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập tên phim trước!")
            return
        info = fetch_movie_info(name)
        if not info:
            messagebox.showerror("Không tìm thấy", "Không tìm thấy phim!")
            return

        self.e_name.delete(0, tk.END)
        self.e_name.insert(0, info.get("title", name))
        self.e_actors.delete(0, tk.END)
        self.e_actors.insert(0, info.get("actors", ""))
        self.e_duration.delete(0, tk.END)
        self.e_duration.insert(0, str(info.get("duration", "")))
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", info.get("overview", ""))

        messagebox.showinfo("Thành công", f"Đã tải dữ liệu phim: {info.get('title')}")

    # =====================================================
    def save_action(self):
        genres = ", ".join(self.lb_genre.get(i) for i in self.lb_genre.curselection())
        success, msg = self.controller.save(
            self.mode, self.movie_id,
            self.e_name.get(),
            self.e_duration.get(),
            self.cbo_country.get(),
            genres,
            self.e_actors.get(),
            self.cbo_lang.get(),
            self.cbo_age.get(),
            self.txt_desc.get("1.0", tk.END),
            self.current_poster_path
        )
        if success:
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Lỗi", msg)
