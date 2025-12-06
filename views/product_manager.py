import tkinter as tk
from tkinter import ttk, messagebox
from controllers.product_controller import ProductController
from views.product_dialog import ProductDialog


class ProductManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = ProductController()
        self.render()

    def render(self):
        # Layout cơ bản
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Toolbar
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))
        tk.Label(toolbar, text="Danh sách sản phẩm", font=("Arial", 14, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        tk.Button(toolbar, text="+ Thêm sản phẩm", bg="#5c6bc0", fg="white", font=("Arial", 10, "bold"),
                  command=lambda: self.open_dialog("add")).pack(side=tk.RIGHT)

        # Table Frame
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=40, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        columns = ("id", "name", "category", "price", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID");
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("name", text="Tên sản phẩm");
        self.tree.column("name", width=200)
        self.tree.heading("category", text="Loại");
        self.tree.column("category", width=100, anchor="center")
        self.tree.heading("price", text="Giá bán");
        self.tree.column("price", width=100, anchor="e")
        self.tree.heading("actions", text="Thao tác");
        self.tree.column("actions", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_click)

        self.load_data()

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        products = self.controller.get_all()
        for p in products:
            price_str = f"{int(p.price):,} đ"
            # Cột actions chứa icon
            self.tree.insert("", tk.END, iid=p.product_id, values=(p.product_id, p.name, p.category, price_str, "✏  🗑"))

    # --- SỬA LỖI TẠI ĐÂY: Phân biệt click Sửa và Xóa ---
    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return

        col = self.tree.identify_column(event.x)

        # Cột actions là cột thứ 5 (#5)
        if col == '#5':
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            # Lấy khung bao quanh ô đó (x, y, width, height)
            bbox = self.tree.bbox(item_id, col)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                relative_x = event.x - cell_x

                # Chia đôi ô: Nửa trái là Sửa, Nửa phải là Xóa
                if relative_x < cell_width / 2:
                    # --- NÚT SỬA ---
                    self.open_dialog("edit", item_id)
                else:
                    # --- NÚT XÓA ---
                    product_name = self.tree.item(item_id, "values")[1]
                    if messagebox.askyesno("Xác nhận", f"Xóa sản phẩm: {product_name}?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", msg)

    def open_dialog(self, mode, p_id=None):
        ProductDialog(self.parent, self.controller, mode, p_id, on_success=self.load_data)