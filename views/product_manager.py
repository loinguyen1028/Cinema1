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

        # 1. TOOLBAR (Tìm kiếm & Thêm mới)
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        # --- KHU VỰC TÌM KIẾM ---
        filter_frame = tk.Frame(toolbar, bg="#f0f2f5")
        filter_frame.pack(side=tk.LEFT)

        # Ô nhập từ khóa
        self.entry_search = tk.Entry(filter_frame, width=30, font=("Arial", 10))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search)  # Tìm ngay khi gõ

        tk.Label(filter_frame, text="🔍", bg="#f0f2f5", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        # Combobox Lọc Loại
        tk.Label(filter_frame, text="Loại:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(15, 5))
        self.cbo_category = ttk.Combobox(filter_frame, state="readonly", width=15)
        self.cbo_category.pack(side=tk.LEFT, ipady=3)
        self.cbo_category.bind("<<ComboboxSelected>>", self.on_search)

        # Nút Thêm Mới
        tk.Button(toolbar, text="+ Thêm sản phẩm", bg="#5c6bc0", fg="white", font=("Arial", 10, "bold"),
                  command=lambda: self.open_dialog("add")).pack(side=tk.RIGHT)

        # 2. TABLE
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

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

        # Load dữ liệu lần đầu
        self.update_categories()
        self.load_data()

    def update_categories(self):
        # Lấy danh sách loại từ DB để nạp vào Combobox
        cats = self.controller.get_categories()
        self.cbo_category['values'] = ["Tất cả"] + cats
        self.cbo_category.current(0)

    def load_data(self):
        # Lấy từ khóa và loại đang chọn
        keyword = self.entry_search.get().strip()
        category = self.cbo_category.get()

        # Gọi controller tìm kiếm
        products = self.controller.search(keyword, category)

        # Xóa cũ & Vẽ mới
        for i in self.tree.get_children(): self.tree.delete(i)

        for p in products:
            price_str = f"{int(p.price):,} đ"
            self.tree.insert("", tk.END, iid=p.product_id, values=(p.product_id, p.name, p.category, price_str, "✏  🗑"))

    def on_search(self, event=None):
        self.load_data()

    def on_click(self, event):
        # ... (Giữ nguyên logic Sửa/Xóa cũ) ...
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        col = self.tree.identify_column(event.x)
        if col == '#5':
            item_id = self.tree.identify_row(event.y)
            if not item_id: return
            bbox = self.tree.bbox(item_id, col)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                if (event.x - cell_x) < cell_width / 2:
                    self.open_dialog("edit", item_id)
                else:
                    p_name = self.tree.item(item_id, "values")[1]
                    if messagebox.askyesno("Xác nhận", f"Xóa: {p_name}?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                            self.update_categories()  # Cập nhật lại list category lỡ xóa mất loại duy nhất
                        else:
                            messagebox.showerror("Lỗi", msg)

    def open_dialog(self, mode, p_id=None):
        # Khi đóng dialog, load lại cả data lẫn category (để cập nhật loại mới thêm)
        def on_done():
            self.load_data()
            self.update_categories()

        ProductDialog(self.parent, self.controller, mode, p_id, on_success=on_done)