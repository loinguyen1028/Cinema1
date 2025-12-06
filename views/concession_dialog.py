import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


class ConcessionDialog(tk.Toplevel):
    def __init__(self, parent, controller, initial_selection=None, on_confirm=None):
        """
        Giao diện chọn món ăn/nước uống dạng POS (Point of Sale)
        """
        super().__init__(parent)
        self.controller = controller
        # Copy giỏ hàng cũ để không ảnh hưởng trực tiếp nếu bấm Hủy
        self.selected_products = {k: v.copy() for k, v in initial_selection.items()} if initial_selection else {}
        self.on_confirm = on_confirm

        self.title("Menu Bắp Nước")
        self.geometry("1100x700")  # Rộng hơn để hiển thị grid đẹp
        self.config(bg="#f0f2f5")
        self.grab_set()

        # Lấy danh sách sản phẩm từ DB thông qua Controller
        # (Lưu ý: Controller phải có hàm get_products gọi xuống DAO)
        self.all_products = self.controller.get_products()

        # Lấy danh sách danh mục (Category) duy nhất từ dữ liệu
        # Thêm mục "Tất cả" lên đầu
        categories_set = set(p.category for p in self.all_products if p.category)
        self.categories = ["Tất cả"] + sorted(list(categories_set))
        self.current_category = "Tất cả"

        self.render_layout()
        self.render_categories()
        self.render_products()

    def render_layout(self):
        # 1. Header & Thanh toán tạm tính
        header_frame = tk.Frame(self, bg="#0f1746", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(header_frame, text="MENU ĐỒ ĂN & THỨC UỐNG", font=("Arial", 14, "bold"), fg="white",
                 bg="#0f1746").pack(side=tk.LEFT, padx=20)

        self.lbl_total = tk.Label(header_frame, text="Đã chọn: 0đ", font=("Arial", 12, "bold"), fg="#ff9800",
                                  bg="#0f1746")
        self.lbl_total.pack(side=tk.RIGHT, padx=20)

        # 2. Container chính (Chia 2 phần: Menu trái & Lưới phải)
        main_body = tk.Frame(self, bg="#f0f2f5")
        main_body.pack(fill=tk.BOTH, expand=True)

        # --- MENU DANH MỤC (BÊN TRÁI) ---
        self.cat_frame = tk.Frame(main_body, bg="white", width=220)
        self.cat_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.cat_frame.pack_propagate(False)  # Cố định chiều rộng cột trái

        tk.Label(self.cat_frame, text="DANH MỤC", font=("Arial", 11, "bold"), bg="white", fg="#555").pack(pady=(20, 10))

        # --- LƯỚI SẢN PHẨM (BÊN PHẢI) ---
        right_frame = tk.Frame(main_body, bg="#f0f2f5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas để cuộn lưới sản phẩm
        self.canvas = tk.Canvas(right_frame, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)

        self.product_grid = tk.Frame(self.canvas, bg="#f0f2f5")

        self.product_grid.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.product_grid, anchor="nw")

        # Tự động resize width của frame trong canvas khi cửa sổ thay đổi
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 3. Footer Buttons
        btn_frame = tk.Frame(self, bg="white", pady=15)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(btn_frame, text="Hủy bỏ", bg="#eee", width=12, relief="flat", font=("Arial", 10),
                  command=self.destroy).pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="Xác nhận chọn", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                  width=15, relief="flat", command=self.confirm_action).pack(side=tk.RIGHT, padx=10)

    def on_canvas_configure(self, event):
        # Giúp frame bên trong canvas giãn ra theo chiều rộng cửa sổ
        self.canvas.itemconfig(self.window_id, width=event.width)

    def render_categories(self):
        # Xóa các nút cũ (nếu có)
        for widget in self.cat_frame.winfo_children():
            if isinstance(widget, tk.Button): widget.destroy()

        self.cat_buttons = {}

        for cat in self.categories:
            # Tạo nút danh mục
            btn = tk.Button(self.cat_frame, text=cat, font=("Arial", 11),
                            bg="white", fg="#333", relief="flat", anchor="w", padx=20, pady=10,
                            activebackground="#e3f2fd", cursor="hand2",
                            command=lambda c=cat: self.switch_category(c))
            btn.pack(fill=tk.X, pady=2)
            self.cat_buttons[cat] = btn

        # Highlight category đang chọn
        self.highlight_category()

    def switch_category(self, category):
        self.current_category = category
        self.highlight_category()
        self.render_products()  # Vẽ lại lưới sản phẩm

    def highlight_category(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.current_category:
                btn.config(bg="#1976d2", fg="white", font=("Arial", 11, "bold"))
            else:
                btn.config(bg="white", fg="#333", font=("Arial", 11, "normal"))

    def render_products(self):
        # Xóa sản phẩm cũ trên lưới
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        # Lọc sản phẩm theo danh mục
        if self.current_category == "Tất cả":
            display_products = self.all_products
        else:
            display_products = [p for p in self.all_products if p.category == self.current_category]

        # Vẽ lưới (Grid System)
        COLUMNS = 4  # Số cột muốn hiển thị trên 1 hàng

        for idx, product in enumerate(display_products):
            row = idx // COLUMNS
            col = idx % COLUMNS

            self.create_product_card(product, row, col)

        self.update_total_label()

    def create_product_card(self, product, row, col):
        # Container cho 1 sản phẩm
        card = tk.Frame(self.product_grid, bg="white", bd=1, relief="solid")

        # Grid config: sticky='nsew' để giãn đều, padx/pady tạo khoảng cách
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Cấu hình grid column weight để các cột đều nhau
        self.product_grid.grid_columnconfigure(col, weight=1)

        # 1. Ảnh sản phẩm
        img_frame = tk.Frame(card, bg="white", height=140)
        img_frame.pack(fill=tk.X)
        img_frame.pack_propagate(False)  # Giữ chiều cao cố định cho ảnh

        lbl_img = tk.Label(img_frame, text="NO IMAGE", bg="#eee", fg="#999")
        lbl_img.pack(fill=tk.BOTH, expand=True)

        if product.image_path and os.path.exists(product.image_path):
            try:
                img = Image.open(product.image_path)
                img = img.resize((140, 140), Image.Resampling.LANCZOS)  # Resize vuông
                photo = ImageTk.PhotoImage(img)
                lbl_img.config(image=photo, text="", bg="white")
                lbl_img.image = photo  # Giữ reference
            except:
                pass

        # 2. Tên & Giá
        info_frame = tk.Frame(card, bg="white", pady=5)
        info_frame.pack(fill=tk.X, padx=10)

        tk.Label(info_frame, text=product.name, font=("Arial", 10, "bold"), bg="white", wraplength=130,
                 anchor="w").pack(fill=tk.X)
        tk.Label(info_frame, text=f"{int(product.price):,} đ", font=("Arial", 11), fg="#e65100", bg="white",
                 anchor="w").pack(fill=tk.X)

        # 3. Bộ điều khiển số lượng ( -  1  + )
        ctrl_frame = tk.Frame(card, bg="white", pady=10)
        ctrl_frame.pack(fill=tk.X)

        # Lấy số lượng hiện tại trong giỏ (nếu có)
        current_qty = 0
        if product.product_id in self.selected_products:
            current_qty = self.selected_products[product.product_id]['qty']

        var_qty = tk.IntVar(value=current_qty)

        # Hàm xử lý tăng giảm
        def change_qty(delta):
            new_q = var_qty.get() + delta
            if new_q < 0: new_q = 0
            if new_q > 50: return  # Max limit

            var_qty.set(new_q)

            if new_q > 0:
                # Cập nhật vào giỏ hàng
                self.selected_products[product.product_id] = {'obj': product, 'qty': new_q}
                # Hiệu ứng đổi màu viền card để biết đã chọn
                card.config(bd=2, relief="solid", highlightbackground="#1976d2", highlightthickness=2)
            else:
                # Xóa khỏi giỏ hàng
                if product.product_id in self.selected_products:
                    del self.selected_products[product.product_id]
                # Trả về màu card thường
                card.config(bd=1, relief="solid", highlightthickness=0)

            self.update_total_label()

        # Nút Trừ
        btn_sub = tk.Button(ctrl_frame, text="-", font=("Arial", 12, "bold"), width=3, bg="#eee", relief="flat",
                            command=lambda: change_qty(-1))
        btn_sub.pack(side=tk.LEFT, padx=(15, 5))

        # Hiển thị số lượng
        lbl_q = tk.Label(ctrl_frame, textvariable=var_qty, font=("Arial", 12, "bold"), bg="white", width=3)
        lbl_q.pack(side=tk.LEFT)

        # Nút Cộng
        btn_add = tk.Button(ctrl_frame, text="+", font=("Arial", 12, "bold"), width=3, bg="#1976d2", fg="white",
                            relief="flat",
                            command=lambda: change_qty(1))
        btn_add.pack(side=tk.RIGHT, padx=(5, 15))

        # Nếu đã chọn từ trước thì highlight card ngay lúc vẽ
        if current_qty > 0:
            card.config(highlightbackground="#1976d2", highlightthickness=2)

    def update_total_label(self):
        total = sum(item['obj'].price * item['qty'] for item in self.selected_products.values())
        count = sum(item['qty'] for item in self.selected_products.values())
        self.lbl_total.config(text=f"Đã chọn ({count} món): {int(total):,} đ")

    def confirm_action(self):
        if self.on_confirm:
            self.on_confirm(self.selected_products)
        self.destroy()