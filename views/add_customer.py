import tkinter as tk
from tkinter import ttk
from controllers.customer_controller import CustomerController
from views.customer_dialog import CustomerDialog


class AddCustomer:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = CustomerController()

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "selected": "#334155",
            "edit": "#2563eb"
        }

        self.action_buttons = []
        self.current_action_row = None

        self.render()

    def render(self):
        for w in self.parent.winfo_children():
            w.destroy()

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="👥 QUẢN LÝ KHÁCH HÀNG",
            font=("Arial", 18, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["bg"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="➕ Thêm khách hàng",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

        toolbar = tk.Frame(container, bg=self.colors["card"], padx=15, pady=12)
        toolbar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            toolbar,
            text="🔍 Tìm theo tên / SĐT:",
            font=("Arial", 11),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(side=tk.LEFT)

        self.entry_search = tk.Entry(toolbar, width=38, font=("Arial", 11), relief="flat")
        self.entry_search.pack(side=tk.LEFT, padx=10, ipady=6)
        self.entry_search.bind("<KeyRelease>", self.on_search)

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

        widths = [60, 200, 130, 240, 120, 80, 120, 130, 100]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("id", "points", "actions") else "w"
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

    def load_data(self):
        self.hide_action_buttons()
        customers = self.controller.get_all()
        self.update_table(customers)

    def on_search(self, event=None):
        keyword = self.entry_search.get().strip()
        customers = self.controller.search(keyword) if keyword else self.controller.get_all()
        self.update_table(customers)

    def update_table(self, customers):
        self.tree.delete(*self.tree.get_children())

        for cus in customers:
            extra = cus.extra_info or {}

            level = cus.tier.tier_name if cus.tier else "Chưa xếp hạng"
            self.tree.insert(
                "",
                tk.END,
                iid=cus.customer_id,
                values=(
                    cus.customer_id,
                    cus.name,
                    cus.phone,
                    cus.email,
                    extra.get("dob", ""),
                    cus.points,
                    level,
                    cus.created_at.strftime("%d/%m/%Y") if cus.created_at else "",
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

        self.action_buttons = [self.btn_edit]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        self.current_action_row = item_id

        bbox = self.tree.bbox(item_id, "#9")
        if not bbox:
            return

        x, y, width, height = bbox

        self.btn_edit.place(
            x=x + 8,
            y=y + 5,
            width=width - 16,
            height=height - 10
        )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    def open_dialog(self, mode, customer_id=None):
        CustomerDialog(
            self.parent,
            self.controller,
            mode,
            customer_id,
            on_success=self.load_data
        )

    def on_edit(self):
        if self.current_action_row:
            self.open_dialog("edit", self.current_action_row)
