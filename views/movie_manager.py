import tkinter as tk
from tkinter import ttk, messagebox
from controllers.movie_controller import MovieController
from views.movie_dialog import MovieDialog
from views.movie_detail import MovieDetail


class MovieManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = MovieController()

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "btn": "#2563eb",
            "selected": "#334155"
        }

        self.action_buttons = []
        self.current_action_row = None

        self.render()

    def render(self):
        for w in self.parent.winfo_children():
            w.destroy()

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # ===== HEADER =====
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="🎬 QUẢN LÝ PHIM",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="+ Thêm phim",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

        # ===== SEARCH BAR =====
        toolbar = tk.Frame(container, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))

        search_frame = tk.Frame(
            toolbar,
            bg=self.colors["panel"],
            highlightbackground=self.colors["primary"],
            highlightthickness=1
        )
        search_frame.pack(side=tk.LEFT)

        self.entry_search = tk.Entry(
            search_frame,
            width=40,
            font=("Arial", 11),
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            insertbackground=self.colors["primary"],
            relief="flat"
        )
        self.entry_search.pack(side=tk.LEFT, ipady=7, padx=(8, 4))
        self.entry_search.insert(0, "Tìm kiếm phim...")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        def clear_ph(e):
            if self.entry_search.get() == "Tìm kiếm phim...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg=self.colors["text"])

        def restore_ph(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Tìm kiếm phim...")
                self.entry_search.config(fg=self.colors["muted"])

        self.entry_search.bind("<FocusIn>", clear_ph)
        self.entry_search.bind("<FocusOut>", restore_ph)

        tk.Label(
            search_frame,
            text="🔍",
            bg=self.colors["panel"],
            fg=self.colors["primary"],
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=(0, 8))

        # ===== TABLE CARD =====
        card = tk.Frame(container, bg=self.colors["card"])
        card.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=44,
            font=("Arial", 11),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["card"],
            foreground=self.colors["primary"],
            font=("Arial", 11, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", self.colors["selected"])],
            foreground=[("selected", "#ffffff")]
        )

        columns = ("id", "name", "genre", "actors", "age", "duration", "actions")
        self.tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = ["ID", "Tên phim", "Thể loại", "Diễn viên", "Tuổi", "Thời lượng", "Thao tác"]
        widths = [60, 220, 150, 220, 70, 110, 160]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col not in ("name", "genre", "actors") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=(col != "actions"))

        self.tree.column("actions", anchor="center", stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_data()

    # ===== LOAD DATA =====
    def load_data(self, movies=None):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        if movies is None:
            movies = self.controller.get_all()

        for m in movies:
            extra = m.extra_info or {}
            self.tree.insert(
                "",
                tk.END,
                iid=m.movie_id,
                values=(
                    m.movie_id,
                    m.title,
                    extra.get("genre", ""),
                    extra.get("actors", ""),
                    extra.get("age_limit", ""),
                    f"{m.duration_min} phút",
                    ""
                )
            )

    # ===== SEARCH =====
    def on_search(self, event=None):
        keyword = self.entry_search.get().strip()

        if keyword == "Tìm kiếm phim...":
            keyword = ""

        movies = (
            self.controller.search(keyword)
            if keyword
            else self.controller.get_all()
        )

        self.load_data(movies)

    # ===== ACTION BUTTONS =====
    def create_action_buttons(self):
        base = {
            "font": ("Arial", 11),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_view = tk.Button(
            self.tree, text="👁", bg="#1e293b", fg="white",
            command=self.on_view, **base
        )
        self.btn_edit = tk.Button(
            self.tree, text="✏", bg="#2563eb", fg="white",
            command=self.on_edit, **base
        )
        self.btn_delete = tk.Button(
            self.tree, text="🗑", bg="#dc2626", fg="white",
            command=self.on_delete, **base
        )

        self.action_buttons = [self.btn_view, self.btn_edit, self.btn_delete]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        self.current_action_row = item_id

        bbox = self.tree.bbox(item_id, "#7")
        if not bbox:
            return

        x, y, width, height = bbox
        part = width // 3

        for i, btn in enumerate(self.action_buttons):
            btn.place(
                x=x + i * part + 2,
                y=y + 4,
                width=part - 4,
                height=height - 8
            )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    # ===== ACTIONS =====
    def on_view(self):
        if self.current_action_row:
            MovieDetail(self.parent, self.controller, self.current_action_row)

    def on_edit(self):
        if self.current_action_row:
            self.open_dialog("edit", self.current_action_row)

    def on_delete(self):
        if not self.current_action_row:
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa phim này?"):
            success, msg = self.controller.delete(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

    def open_dialog(self, mode="add", movie_id=None):
        MovieDialog(
            self.parent,
            self.controller,
            mode,
            movie_id,
            on_success=self.load_data
        )
