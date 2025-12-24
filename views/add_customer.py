import tkinter as tk
from tkinter import ttk, messagebox
from controllers.customer_controller import CustomerController
from views.customer_dialog import CustomerDialog


class AddCustomer:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = CustomerController()
        self.render()

    def render(self):
        # ================= ROOT =================
        content = tk.Frame(self.parent, bg="#121212")
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # ================= HEADER =================
        header = tk.Frame(content, bg="#121212")
        header.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header,
            text="👥 QUẢN LÝ KHÁCH HÀNG",
            font=("Arial", 18, "bold"),
            fg="#f5c518",
            bg="#121212"
        ).pack(side=tk.LEFT)

        # ================= TOOLBAR =================
        toolbar = tk.Frame(content, bg="#1a1a1a", padx=15, pady=10)
        toolbar.pack(fill=tk.X, pady=(0, 15))

        # --- Search ---
        search_frame = tk.Frame(toolbar, bg="#1a1a1a")
        search_frame.pack(side=tk.LEFT)

        self.entry_search = tk.Entry(
            search_frame,
            width=38,
            font=("Arial", 11),
            relief="flat"
        )
        self.entry_search.pack(side=tk.LEFT, ipady=6)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        tk.Label(
            search_frame,
            text="🔍 Tìm theo tên / SĐT",
            font=("Arial", 10),
            bg="#1a1a1a",
            fg="#aaaaaa"
        ).pack(side=tk.LEFT, padx=8)

        # --- Add button ---
        tk.Button(
            toolbar,
            text="➕ Thêm khách hàng",
            bg="#f5c518",
            fg="black",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=18,
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

        # ================= TABLE =================
        table_frame = tk.Frame(content, bg="#1a1a1a")
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1a1a1a",
            foreground="white",
            rowheight=36,
            fieldbackground="#1a1a1a",
            borderwidth=0,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            background="#202020",
            foreground="#f5c518",
            font=("Arial", 11, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#f5c518")],
            foreground=[("selected", "black")]
        )

        columns = ("id", "name", "phone", "email", "dob", "points", "level", "created_at", "actions")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = [
            "ID", "Tên khách hàng", "SĐT", "Email",
            "Ngày sinh", "Điểm", "Hạng", "Ngày tạo", "Thao tác"
        ]
        widths = [50, 180, 120, 220, 110, 70, 100, 120, 90]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("id", "points", "actions") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        self.load_data()

    # ================= DATA =================
    def load_data(self):
        customers = self.controller.get_all()
        self.update_table(customers)

    def on_search(self, event):
        keyword = self.entry_search.get().strip()
        if keyword:
            customers = self.controller.search(keyword)
        else:
            customers = self.controller.get_all()
        self.update_table(customers)

    def update_table(self, customers):
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_icons = "✏"
        for cus in customers:
            extra = cus.extra_info if cus.extra_info else {}
            dob = extra.get("dob", "")
            points = extra.get("points", 0)
            level = extra.get("level", "Thân thiết")

            created = cus.created_at.strftime("%d/%m/%Y") if cus.created_at else ""

            vals = (
                cus.customer_id,
                cus.name,
                cus.phone,
                cus.email,
                dob,
                points,
                level,
                created,
                action_icons
            )

            self.tree.insert("", tk.END, iid=cus.customer_id, values=vals)

    # ================= ACTION =================
    def open_dialog(self, mode, customer_id=None):
        CustomerDialog(
            self.parent,
            self.controller,
            mode,
            customer_id,
            on_success=self.load_data
        )

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column == "#9":
            item_id = self.tree.identify_row(event.y)
            if not item_id:
                return

            self.open_dialog("edit", item_id)
