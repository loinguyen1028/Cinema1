import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from controllers.movie_controller import MovieController
from views.movie_dialog import MovieDialog
from views.movie_detail import MovieDetail

class MovieManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = MovieController()
        self.render()

    def render(self):
        # --- Container & Toolbar (Giữ nguyên) ---
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        tk.Label(search_frame, text="Tìm kiếm", bg="#f0f2f5", fg="#666").pack(anchor="w")

        self.entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search_key_release)

        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # Nút Thêm (Gọi open_dialog)
        btn_add = tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white",
                            font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat", cursor="hand2",
                            command=lambda: self.open_dialog(mode="add"))
        btn_add.pack(side=tk.RIGHT)

        # --- Table ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=45, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        columns = ("id", "name", "genre", "actors", "age_limit", "duration", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["ID", "Tên phim", "Thể loại", "Diễn viên", "Tuổi", "Thời lượng", "Thao tác"]
        for col, h in zip(columns, headers):
            self.tree.heading(col, text=h, anchor="center" if col != "name" and col != "actors" else "w")

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

    # --- Logic ---
    def load_data(self):
        movies = self.controller.get_all()
        self.update_table(movies)

    def on_search_key_release(self, event):
        keyword = self.entry_search.get().strip()
        movies = self.controller.search(keyword)
        self.update_table(movies)

    def update_table(self, movies):
        for item in self.tree.get_children():
            self.tree.delete(item)
        action_btns = "👁       ✏       🗑"
        for m in movies:
            extra = m.extra_info if m.extra_info else {}
            vals = (m.movie_id, m.title, extra.get('genre', ''), extra.get('actors', ''),
                    extra.get('age_limit', ''), m.duration_min, action_btns)
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
                rel_x = event.x - cell_x
                if rel_x < cell_width / 3:
                    MovieDetail(self.parent, self.controller, item_id)
                elif rel_x < (cell_width / 3) * 2:
                    self.open_dialog(mode="edit", movie_id=item_id)
                else:
                    if messagebox.askyesno("Xác nhận", "Xóa phim này?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", msg)

    # --- MỞ DIALOG TỪ FILE RIÊNG ---
    def open_dialog(self, mode="add", movie_id=None):
        # Gọi class MovieDialog và truyền hàm load_data vào để nó tự refresh khi lưu xong
        MovieDialog(self.parent, self.controller, mode, movie_id, on_success=self.load_data)