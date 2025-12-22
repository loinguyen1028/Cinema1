import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
from PIL import Image, ImageTk

# --- IMPORT HÀM LẤY DỮ LIỆU ---
# Đảm bảo bạn đã tạo file utils/omdb_helper.py (hoặc tmdb_helper.py)
try:
    from utils.omdb_helper import fetch_movie_info
except ImportError:
    # Fallback nếu chưa tạo file helper để không lỗi chương trình
    def fetch_movie_info(name):
        return None


class MovieDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", movie_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.movie_id = movie_id
        self.on_success = on_success

        self.title("Thêm phim mới" if mode == "add" else "Chỉnh sửa phim")
        self.geometry("900x700")
        self.config(bg="#f5f6f8")
        self.grab_set()

        self.current_poster_path = ""
        self.movie_data = self.load_initial_data()
        self.render_ui()

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
                data["desc"] = movie.description if movie.description else ""
                if movie.poster_path: self.current_poster_path = movie.poster_path

                extra = movie.extra_info if movie.extra_info else {}
                data["genre"] = extra.get('genre', '')
                data["country"] = extra.get('country', 'Mỹ')
                data["actors"] = extra.get('actors', '')
                data["lang"] = extra.get('language', 'Lồng tiếng')
                data["age"] = extra.get('age_limit', '16')
        return data

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        tk.Label(container, text=self.title(), font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # --- ROW 1: TÊN PHIM (CÓ NÚT AUTO) & THỂ LOẠI ---
        row1 = tk.Frame(container, bg="#f5f6f8")
        row1.pack(fill=tk.X, pady=5)

        # Cụm Tên Phim (Thay vì dùng create_input, ta tự vẽ để chèn nút Button)
        f_name_container = tk.Frame(row1, bg="#f5f6f8")
        f_name_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(f_name_container, text="Tên phim", bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")

        f_input_line = tk.Frame(f_name_container, bg="#f5f6f8")
        f_input_line.pack(fill=tk.X, pady=2)

        self.e_name = tk.Entry(f_input_line, font=("Arial", 11), relief="flat", highlightthickness=1,
                               highlightbackground="#ccc")
        self.e_name.insert(0, self.movie_data["name"])
        self.e_name.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        # NÚT AUTO FILL (MỚI)
        tk.Button(f_input_line, text="⚡ Auto", bg="#FFD700", fg="#333",
                  font=("Arial", 9, "bold"), relief="flat",
                  command=self.auto_fill_data).pack(side=tk.RIGHT, padx=(5, 0), ipady=1)

        # Cụm Thể loại (Bên phải)
        f_genre = tk.Frame(row1, bg="#f5f6f8", width=250)
        f_genre.pack(side=tk.RIGHT, padx=(20, 0), fill=tk.Y)
        tk.Label(f_genre, text="Thể loại", bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        list_frame = tk.Frame(f_genre, bg="white", bd=1, relief="solid")
        list_frame.pack(fill=tk.X, pady=2)

        self.genres_list_items = ["Hành động", "Kinh dị", "Tình cảm", "Hài", "Hoạt hình", "Viễn tưởng", "Tâm lý",
                                  "Gia đình"]
        self.lb_genre = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=4, font=("Arial", 10),
                                   exportselection=False, bd=0)
        self.lb_genre.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Set selected genres
        curr_genres = [g.strip() for g in self.movie_data["genre"].split(",")]
        for item in self.genres_list_items:
            self.lb_genre.insert(tk.END, item)
            if item in curr_genres: self.lb_genre.selection_set(tk.END)

        # --- ROW 2 ---
        row2 = tk.Frame(container, bg="#f5f6f8")
        row2.pack(fill=tk.X, pady=10)
        self.e_actors = self.create_input(row2, "Diễn viên", self.movie_data["actors"], side=tk.LEFT)

        right_row2 = tk.Frame(row2, bg="#f5f6f8")
        right_row2.pack(side=tk.RIGHT, padx=(20, 0))
        self.e_duration = self.create_input(right_row2, "Thời lượng (phút)", self.movie_data["duration"], side=tk.LEFT,
                                            width=15)
        self.cbo_country = self.create_combo(right_row2, "Quốc gia", self.movie_data["country"],
                                             ["Việt Nam", "Mỹ", "Hàn Quốc", "Thái Lan"], side=tk.LEFT, width=18)

        # --- ROW 3 ---
        row3 = tk.Frame(container, bg="#f5f6f8")
        row3.pack(fill=tk.X, pady=10)
        self.cbo_lang = self.create_combo(row3, "Hình thức", self.movie_data["lang"],
                                          ["Lồng tiếng", "Phụ đề", "Thuyết minh"], side=tk.LEFT, width=50)

        right_row3 = tk.Frame(row3, bg="#f5f6f8")
        right_row3.pack(side=tk.RIGHT, padx=(20, 0))
        self.cbo_age = self.create_combo(right_row3, "Giới hạn tuổi", self.movie_data["age"], ["P", "13", "16", "18"],
                                         side=tk.LEFT, width=25)

        # --- ROW 4 ---
        row4 = tk.Frame(container, bg="#f5f6f8")
        row4.pack(fill=tk.BOTH, expand=True, pady=10)

        f_desc = tk.Frame(row4, bg="#f5f6f8")
        f_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(f_desc, text="Mô tả", bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")

        txt_frame = tk.Frame(f_desc, bg="white", bd=1, relief="solid")
        txt_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        scrollbar = tk.Scrollbar(txt_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_desc = tk.Text(txt_frame, font=("Arial", 11), height=8, relief="flat", yscrollcommand=scrollbar.set,
                                bd=0)
        self.txt_desc.insert("1.0", self.movie_data["desc"])
        self.txt_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.txt_desc.yview)

        right_col = tk.Frame(row4, bg="#f5f6f8", width=200)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        poster_frame = tk.Frame(right_col, bg="#ddd", height=150, width=120)
        poster_frame.pack(anchor="n", pady=(20, 5))
        poster_frame.pack_propagate(False)
        self.lbl_poster_display = tk.Label(poster_frame, text="[ POSTER ]", bg="#ddd", fg="#666")
        self.lbl_poster_display.pack(expand=True, fill=tk.BOTH)
        self.lbl_path_display = tk.Label(right_col, text="Chưa chọn ảnh", bg="#f5f6f8", fg="#666", font=("Arial", 8),
                                         wraplength=180)
        self.lbl_path_display.pack(anchor="n", pady=(0, 5))

        tk.Button(right_col, text="📂 Ảnh", bg="#1976d2", fg="white", relief="flat", font=("Arial", 9),
                  command=self.choose_image).pack(anchor="n")
        if self.current_poster_path: self.load_image_to_label(self.current_poster_path)

        tk.Button(right_col, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=15, relief="flat",
                  command=self.save_action).pack(side=tk.BOTTOM, pady=10)

    # --- LOGIC AUTO FILL (MỚI) ---
    def auto_fill_data(self):
        movie_name = self.e_name.get().strip()
        if not movie_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên phim (tiếng Anh hoặc Việt)!")
            return

        try:
            # Gọi API
            info = fetch_movie_info(movie_name)

            if not info:
                messagebox.showerror("Thất bại", "Không tìm thấy phim này trên hệ thống!")
                return

            # 1. Điền Tên (Chuẩn hóa)
            if info.get('title'):
                self.e_name.delete(0, tk.END)
                self.e_name.insert(0, info['title'])

            # 2. Điền Diễn viên
            if info.get('actors'):
                self.e_actors.delete(0, tk.END)
                self.e_actors.insert(0, info['actors'])

            # 3. Điền Thời lượng
            if info.get('duration'):
                self.e_duration.delete(0, tk.END)
                self.e_duration.insert(0, str(info['duration']))

            # 4. Điền Mô tả
            if info.get('overview'):
                self.txt_desc.delete("1.0", tk.END)
                self.txt_desc.insert("1.0", info['overview'])

            # 5. Xử lý Thể loại (Map Tiếng Anh -> Tiếng Việt)
            api_genres = info.get('genre', '')  # VD: "Action, Adventure, Sci-Fi"

            # Từ điển dịch (Nếu dùng OMDb trả về tiếng Anh)
            genre_map = {
                "Action": "Hành động", "Horror": "Kinh dị", "Romance": "Tình cảm",
                "Comedy": "Hài", "Animation": "Hoạt hình", "Sci-Fi": "Viễn tưởng",
                "Drama": "Tâm lý", "Family": "Gia đình", "Thriller": "Kinh dị"
            }

            # Xóa chọn cũ
            self.lb_genre.selection_clear(0, tk.END)

            # Duyệt qua từng thể loại trong Listbox của mình
            # Nếu chuỗi API chứa từ khóa tương ứng -> Chọn nó
            for i, item_vn in enumerate(self.genres_list_items):
                # Kiểm tra nếu API trả về tiếng Việt (TMDB) giống hệt
                if item_vn.lower() in api_genres.lower():
                    self.lb_genre.selection_set(i)
                    continue

                # Kiểm tra mapping tiếng Anh (OMDb)
                # Tìm key tiếng Anh ứng với item_vn (Action -> Hành động)
                for eng_key, vn_val in genre_map.items():
                    if vn_val == item_vn and eng_key.lower() in api_genres.lower():
                        self.lb_genre.selection_set(i)
                        break

            messagebox.showinfo("Thành công", f"Đã tìm thấy: {info['title']}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    # --- CÁC HÀM CŨ GIỮ NGUYÊN ---
    def load_image_to_label(self, path):
        if not path or not os.path.exists(path):
            self.lbl_poster_display.config(image="", text="[ POSTER ]", bg="#ddd")
            return
        try:
            img = Image.open(path)
            img = img.resize((120, 150), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.lbl_poster_display.config(image=img_tk, text="", bg="#f5f6f8")
            self.lbl_poster_display.image = img_tk
            self.lbl_path_display.config(text=os.path.basename(path))
        except Exception:
            pass

    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.current_poster_path = file_path
            self.load_image_to_label(file_path)

    def save_action(self):
        name = self.e_name.get()
        dur = self.e_duration.get()
        cou = self.cbo_country.get()
        actors = self.e_actors.get()
        lang = self.cbo_lang.get()
        age = self.cbo_age.get()
        desc = self.txt_desc.get("1.0", tk.END)

        selected_indices = self.lb_genre.curselection()
        selected_genres = [self.lb_genre.get(i) for i in selected_indices]
        gen_str = ", ".join(selected_genres)

        success, msg = self.controller.save(
            self.mode, self.movie_id, name, dur, cou, gen_str,
            actors, lang, age, desc, self.current_poster_path
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Thông báo", msg)

    def create_input(self, parent, label, val, side, width=None):
        f = tk.Frame(parent, bg="#f5f6f8")
        f.pack(side=side, fill=tk.X, expand=(width is None))
        if width: f.config(width=width)
        tk.Label(f, text=label, bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        e = tk.Entry(f, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#ccc",
                     width=width)
        e.insert(0, str(val))
        e.pack(fill=tk.X, ipady=4, pady=2)
        return e

    def create_combo(self, parent, label, val, values, side, width=None):
        f = tk.Frame(parent, bg="#f5f6f8")
        f.pack(side=side, fill=tk.X, expand=(width is None))
        tk.Label(f, text=label, bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        c = ttk.Combobox(f, values=values, font=("Arial", 11), width=width)
        c.set(val)
        c.pack(fill=tk.X, ipady=4, pady=2)
        return c