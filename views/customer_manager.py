import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from controllers.customer_controller import CustomerController
from views.customer_dialog import CustomerDialog


class CustomerManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = CustomerController()
        self.render()

    def render(self):
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        # Search
        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        self.entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search)  # Tìm kiếm ngay khi gõ

        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # Button Add
        btn_add = tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white",
                            font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat", cursor="hand2",
                            command=lambda: self.open_dialog("add"))
        btn_add.pack(side=tk.RIGHT)

        # --- Table ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "phone", "email", "dob", "points", "level", "created_at", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["ID", "Tên khách hàng", "SĐT", "Email", "Ngày sinh", "Điểm", "Hạng", "Ngày tạo", "Thao tác"]
        widths = [40, 150, 100, 180, 90, 60, 80, 120, 80]

        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h, anchor="w" if col != "actions" else "center")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        self.load_data()

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

        action_icons = "✏  🗑"
        for cus in customers:
            extra = cus.extra_info if cus.extra_info else {}
            dob = extra.get("dob", "")

            points = cus.points

            # Lấy tên hạng qua relationship (cần xử lý nếu tier bị Null)
            level = cus.tier.tier_name if cus.tier else "Chưa xếp hạng"
            # --------------------

            created = cus.created_at.strftime("%d/%m/%Y") if cus.created_at else ""

            vals = (cus.customer_id, cus.name, cus.phone, cus.email, dob, points, level, created, action_icons)
            self.tree.insert("", tk.END, iid=cus.customer_id, values=vals)

    def open_dialog(self, mode, customer_id=None):
        CustomerDialog(self.parent, self.controller, mode, customer_id, on_success=self.load_data)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return

        column = self.tree.identify_column(event.x)
        # Cột actions là cột thứ 9 (#9)
        if column == '#9':
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            bbox = self.tree.bbox(item_id, column)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                relative_x = event.x - cell_x

                # Logic chia đôi ô (Sửa | Xóa)
                if relative_x < cell_width / 2:
                    # Sửa
                    self.open_dialog("edit", item_id)
                else:
                    # Xóa
                    customer_name = self.tree.item(item_id, "values")[1]
                    if messagebox.askyesno("Xác nhận", f"Xóa khách hàng {customer_name}?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", msg)