import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from dao.movie_dao import MovieDAO

class MovieManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.movie_dao = MovieDAO()
        self.render()

    def render(self):
        # --- Container chính ---
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))
        
        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        tk.Label(search_frame, text="Tìm kiếm", bg="#f0f2f5", fg="#666").pack(anchor="w")
        
        self.entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search_key_release)
        
        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        btn_add = tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white", 
                            font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat", cursor="hand2",
                            command=lambda: self.open_dialog(mode="add"))
        btn_add.pack(side=tk.RIGHT)

        # --- Table Frame ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=45, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        columns = ("id", "name", "genre", "actors", "age_limit", "duration", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("name", text="Tên phim", anchor="w")
        self.tree.heading("genre", text="Thể loại", anchor="w")
        self.tree.heading("actors", text="Diễn viên", anchor="w")
        self.tree.heading("age_limit", text="Tuổi", anchor="center")
        self.tree.heading("duration", text="Thời lượng", anchor="center")
        self.tree.heading("actions", text="Thao tác", anchor="center")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("genre", width=120, anchor="w")
        self.tree.column("actors", width=150, anchor="w")
        self.tree.column("age_limit", width=60, anchor="center")
        self.tree.column("duration", width=80, anchor="center")
        self.tree.column("actions", width=120, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        self.load_data()

    def load_data(self):
        movies = self.movie_dao.get_all_movies()
        self.update_table(movies)

    def on_search_key_release(self, event):
        keyword = self.entry_search.get().strip()
        if keyword:
            movies = self.movie_dao.search_movies(keyword)
        else:
            movies = self.movie_dao.get_all_movies()
        self.update_table(movies)

    def update_table(self, movies):
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_btns = "👁       ✏       🗑"

        for m in movies:
            extra = m.extra_info if m.extra_info else {}
            genre = extra.get('genre', '')
            actors = extra.get('actors', '')
            age = extra.get('age_limit', '')
            
            vals = (m.movie_id, m.title, genre, actors, age, m.duration_min, action_btns)
            self.tree.insert("", tk.END, iid=m.movie_id, values=vals)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)
        if column == '#7': 
            item_id = self.tree.identify_row(event.y)
            if not item_id: return
            bbox = self.tree.bbox(item_id, column)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                relative_x = event.x - cell_x
                section_width = cell_width / 3
                if relative_x < section_width:
                    messagebox.showinfo("Chi tiết", f"ID phim: {item_id}")
                elif relative_x < section_width * 2:
                    self.open_dialog(mode="edit", movie_id=item_id)
                else:
                    if messagebox.askyesno("Xác nhận", "Xóa phim này?"):
                        if self.movie_dao.delete_movie(item_id):
                            messagebox.showinfo("Thành công", "Đã xóa phim!")
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", "Không thể xóa.")

    # ---------------------------------------------------------
    # DIALOG THÊM / SỬA PHIM
    # ---------------------------------------------------------
    def open_dialog(self, mode="add", movie_id=None):
        dialog = tk.Toplevel(self.parent)
        title = "Thêm phim mới" if mode == "add" else "Chỉnh sửa phim"
        dialog.title(title)
        dialog.geometry("900x700")
        dialog.config(bg="#f5f6f8")
        dialog.grab_set()

        val_name = ""
        val_genre_str = ""
        val_actors = ""
        val_lang = "Lồng tiếng"
        val_age = "16"
        val_duration = ""
        val_country = "Mỹ"
        val_desc = ""

        if mode == "edit" and movie_id:
            curr_vals = self.tree.item(movie_id, "values") 
            val_name = curr_vals[1]
            val_genre_str = curr_vals[2]
            val_actors = curr_vals[3]
            val_age = curr_vals[4]
            val_duration = curr_vals[5]

        container = tk.Frame(dialog, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        tk.Label(container, text=title, font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w", pady=(0, 20))

        # --- ROW 1: Tên phim & Thể loại ---
        row1 = tk.Frame(container, bg="#f5f6f8"); row1.pack(fill=tk.X, pady=5)
        e_name = self.create_input(row1, "Tên phim", val_name, side=tk.LEFT)
        
        f_genre = tk.Frame(row1, bg="#f5f6f8", width=250)
        f_genre.pack(side=tk.RIGHT, padx=(20, 0), fill=tk.Y)
        tk.Label(f_genre, text="Thể loại", bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        list_frame = tk.Frame(f_genre, bg="white", bd=1, relief="solid")
        list_frame.pack(fill=tk.X, pady=2)
        
        genres_list = ["Hành động", "Kinh dị", "Tình cảm", "Hài", "Hoạt hình", "Viễn tưởng", "Tâm lý", "Gia đình"]
        lb_genre = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=4, font=("Arial", 10), exportselection=False, bd=0)
        lb_genre.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=lb_genre.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lb_genre.config(yscrollcommand=scrollbar.set)
        
        curr_genres = [g.strip() for g in val_genre_str.split(",")]
        for item in genres_list:
            lb_genre.insert(tk.END, item)
            if item in curr_genres:
                lb_genre.selection_set(tk.END)

        # --- ROW 2: Diễn viên & (Thời lượng + Quốc gia) ---
        row2 = tk.Frame(container, bg="#f5f6f8"); row2.pack(fill=tk.X, pady=10)
        
        e_actors = self.create_input(row2, "Diễn viên", val_actors, side=tk.LEFT)
        
        # Phần bên phải Row 2: Chứa Thời lượng và Quốc gia
        right_row2 = tk.Frame(row2, bg="#f5f6f8")
        right_row2.pack(side=tk.RIGHT, padx=(20, 0))
        
        # 1. Thời lượng (ĐÃ SỬA: Thêm vào đây)
        e_duration = self.create_input(right_row2, "Thời lượng (phút)", val_duration, side=tk.LEFT, width=15)
        
        # 2. Quốc gia
        cbo_country = self.create_combo(right_row2, "Quốc gia", val_country, ["Việt Nam", "Mỹ", "Hàn Quốc", "Thái Lan"], side=tk.LEFT, width=18)

        # --- ROW 3: Hình thức & Giới hạn tuổi ---
        row3 = tk.Frame(container, bg="#f5f6f8"); row3.pack(fill=tk.X, pady=10)
        cbo_lang = self.create_combo(row3, "Hình thức", val_lang, ["Lồng tiếng", "Phụ đề", "Thuyết minh"], side=tk.LEFT, width=50)
        
        right_row3 = tk.Frame(row3, bg="#f5f6f8"); right_row3.pack(side=tk.RIGHT, padx=(20, 0))
        cbo_age = self.create_combo(right_row3, "Giới hạn tuổi", val_age, ["P", "13", "16", "18"], side=tk.LEFT, width=25)

        # --- ROW 4: Mô tả & Ảnh ---
        row4 = tk.Frame(container, bg="#f5f6f8"); row4.pack(fill=tk.BOTH, expand=True, pady=10)
        f_desc = tk.Frame(row4, bg="#f5f6f8")
        f_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(f_desc, text="Mô tả", bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        txt_desc = tk.Text(f_desc, font=("Arial", 11), height=8, relief="flat", highlightthickness=1, highlightbackground="#ccc")
        txt_desc.insert("1.0", val_desc)
        txt_desc.pack(fill=tk.BOTH, expand=True, pady=2)

        right_col = tk.Frame(row4, bg="#f5f6f8", width=200)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        poster_frame = tk.Frame(right_col, bg="#ddd", height=150, width=120)
        poster_frame.pack(anchor="n", pady=(20, 5))
        poster_frame.pack_propagate(False)
        tk.Label(poster_frame, text="[ POSTER ]", bg="#ddd", fg="#666").pack(expand=True)
        tk.Button(right_col, text="📂 Ảnh", bg="#1976d2", fg="white", relief="flat", font=("Arial", 9)).pack(anchor="n")

        btn_save = tk.Button(right_col, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 11, "bold"), 
                             width=15, relief="flat", command=lambda: save_action())
        btn_save.pack(side=tk.BOTTOM, pady=10)

        # --- LOGIC LƯU ---
        def save_action():
            name = e_name.get().strip()
            # Lấy dữ liệu từ ô Thời lượng
            dur = e_duration.get().strip()
            
            cou = cbo_country.get()
            actors = e_actors.get().strip()
            lang = cbo_lang.get()
            age = cbo_age.get()
            desc = txt_desc.get("1.0", tk.END).strip()

            selected_indices = lb_genre.curselection()
            selected_genres = [lb_genre.get(i) for i in selected_indices]
            gen_str = ", ".join(selected_genres)

            if not name:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Tên phim!")
                return
            
            if not dur:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Thời lượng!")
                return

            if not dur.isdigit():
                messagebox.showwarning("Lỗi", "Thời lượng phải là số nguyên (phút)!")
                return

            if mode == "add":
                success = self.movie_dao.add_movie(name, dur, cou, gen_str, actors, lang, age, desc)
                msg = "Thêm mới"
            else:
                success = self.movie_dao.update_movie(movie_id, name, dur, cou, gen_str, actors, lang, age, desc)
                msg = "Cập nhật"

            if success:
                messagebox.showinfo("Thành công", f"{msg} phim thành công!")
                self.load_data()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", f"{msg} thất bại!")

    # Helper functions
    def create_input(self, parent, label, val, side, width=None):
        f = tk.Frame(parent, bg="#f5f6f8")
        f.pack(side=side, fill=tk.X, expand=(width is None))
        if width: f.config(width=width) # Bỏ pack_propagate để nó co giãn đẹp hơn với width nhỏ
        tk.Label(f, text=label, bg="#f5f6f8", fg="#555", font=("Arial", 9)).pack(anchor="w")
        e = tk.Entry(f, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#ccc", width=width)
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