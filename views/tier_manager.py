import tkinter as tk
from tkinter import ttk, messagebox
from controllers.tier_controller import TierController
from views.tier_dialog import TierDialog


class TierManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = TierController()
        self.render()

    def render(self):
        # Xóa nội dung cũ trong frame cha
        for widget in self.parent.winfo_children():
            widget.destroy()

        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        tk.Label(toolbar, text="Quản lý Hạng Thành Viên", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        btn_add = tk.Button(toolbar, text="Thêm Hạng", bg="#5c6bc0", fg="white",
                            font=("Arial", 10, "bold"), padx=15, pady=5, relief="flat",
                            command=lambda: self.open_dialog("add"))
        btn_add.pack(side=tk.RIGHT)

        # --- Table ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "point", "discount", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")

        self.tree.heading("name", text="Tên hạng")
        self.tree.column("name", width=200)

        self.tree.heading("point", text="Điểm tối thiểu")
        self.tree.column("point", width=150, anchor="center")

        self.tree.heading("discount", text="Giảm giá (%)")
        self.tree.column("discount", width=150, anchor="center")

        self.tree.heading("actions", text="Thao tác")
        self.tree.column("actions", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        self.load_data()

    def load_data(self):
        tiers = self.controller.get_all()
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_icons = "✏  🗑"
        for t in tiers:
            vals = (t.id, t.tier_name, f"{t.min_point:,}", f"{t.discount_percent}%", action_icons)
            self.tree.insert("", tk.END, iid=t.id, values=vals)

    def open_dialog(self, mode, tier_id=None):
        TierDialog(self.parent, self.controller, mode, tier_id, on_success=self.load_data)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return

        # Cột actions là cột thứ 5 (#5)
        column = self.tree.identify_column(event.x)
        if column == '#5':
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            # Logic chia đôi ô để bấm nút
            bbox = self.tree.bbox(item_id, column)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                relative_x = event.x - cell_x

                if relative_x < cell_width / 2:  # Bấm bên trái -> Sửa
                    self.open_dialog("edit", item_id)
                else:  # Bấm bên phải -> Xóa
                    name = self.tree.item(item_id, "values")[1]
                    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa hạng '{name}'?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", msg)