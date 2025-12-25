import tkinter as tk
from tkinter import ttk, messagebox
from controllers.customer_controller import CustomerController
from views.customer_dialog import CustomerDialog


class CustomerManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = CustomerController()

        self.current_action_row = None
        self.action_buttons = []

        self.render()

    def render(self):
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444",
            "edit": "#2563eb",
            "selected": "#1e3a8a"
        }

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="👥 QUẢN LÝ KHÁCH HÀNG",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="+ Thêm khách hàng",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

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
            width=38,
            font=("Arial", 11),
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            insertbackground=self.colors["primary"],
            relief="flat"
        )
        self.entry_search.pack(side=tk.LEFT, ipady=7, padx=(8, 4))
        self.entry_search.insert(0, "Tìm kiếm...")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        def clear_ph(e):
            if self.entry_search.get() == "Tìm kiếm...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg=self.colors["text"])

        def restore_ph(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Tìm kiếm...")
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

        card = tk.Frame(container, bg=self.colors["card"])
        card.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=38,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["card"],
            foreground=self.colors["primary"],
            font=("Arial", 11, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", self.colors["selected"])],
            foreground=[("selected", "#ffffff")]
        )

        columns = (
            "id", "name", "phone", "email",
            "dob", "points", "level", "created", "actions"
        )

        self.tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = [
            "ID", "Tên khách hàng", "SĐT", "Email",
            "Ngày sinh", "Điểm", "Hạng", "Ngày tạo", "Thao tác"
        ]

        widths = [60, 200, 120, 240, 110, 80, 140, 120, 160]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("id", "points", "actions") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=(col != "actions"))

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_data()

    def load_data(self):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        customers = self.controller.get_all()

        for c in customers:
            extra = c.extra_info or {}
            created = c.created_at.strftime("%d/%m/%Y") if c.created_at else ""
            level = c.tier.tier_name if c.tier else "Chưa xếp hạng"

            self.tree.insert(
                "",
                tk.END,
                iid=c.customer_id,
                values=(
                    c.customer_id,
                    c.name,
                    c.phone,
                    c.email,
                    extra.get("dob", ""),
                    c.points,
                    level,
                    created,
                    ""
                )
            )

    def create_action_buttons(self):
        base = {
            "font": ("Arial", 11),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_edit = tk.Button(
            self.tree,
            text="✏",
            bg=self.colors["edit"],
            fg="white",
            command=self.on_edit,
            **base
        )

        self.btn_delete = tk.Button(
            self.tree,
            text="🗑",
            bg=self.colors["danger"],
            fg="white",
            command=self.on_delete,
            **base
        )

        self.action_buttons = [self.btn_edit, self.btn_delete]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        self.current_action_row = selected[0]

        bbox = self.tree.bbox(self.current_action_row, "#9")
        if not bbox:
            return

        x, y, width, height = bbox
        part = width // 2

        for i, btn in enumerate(self.action_buttons):
            btn.place(
                x=x + i * part + 4,
                y=y + 4,
                width=part - 8,
                height=height - 8
            )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    def on_edit(self):
        if self.current_action_row:
            self.open_dialog("edit", self.current_action_row)

    def on_delete(self):
        if not self.current_action_row:
            return

        name = self.tree.item(self.current_action_row, "values")[1]
        if messagebox.askyesno("Xác nhận", f"Xóa khách hàng: {name}?"):
            success, msg = self.controller.delete(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

    def open_dialog(self, mode, customer_id=None):
        CustomerDialog(
            self.parent,
            self.controller,
            mode,
            customer_id,
            on_success=self.load_data
        )

    def on_search(self, event=None):
        keyword = self.entry_search.get().strip()
        customers = self.controller.search(keyword) if keyword else self.controller.get_all()
        self.load_data()
