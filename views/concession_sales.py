import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from controllers.product_controller import ProductController


class ConcessionSales:
    def __init__(self, parent_frame, user_id):
        self.parent = parent_frame
        self.user_id = user_id
        self.controller = ProductController()

        # Giỏ hàng: {product_id: {'obj': product, 'qty': 1}}
        self.cart = {}

        # Lấy dữ liệu
        self.all_products = self.controller.get_all()
        categories_set = set(p.category for p in self.all_products if p.category)
        self.categories = ["Tất cả"] + sorted(list(categories_set))
        self.current_category = "Tất cả"

        self.render()

    def render(self):
        # Container chính (Chia 3 cột: Danh mục | Sản phẩm | Giỏ hàng)
        main_container = tk.Frame(self.parent, bg="#f0f2f5")
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. CỘT TRÁI: DANH MỤC
        cat_panel = tk.Frame(main_container, bg="white", width=180)
        cat_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        cat_panel.pack_propagate(False)

        tk.Label(cat_panel, text="DANH MỤC", font=("Arial", 11, "bold"), bg="white", fg="#555").pack(pady=20)

        self.cat_buttons = {}
        for cat in self.categories:
            btn = tk.Button(cat_panel, text=cat, font=("Arial", 10),
                            bg="white", fg="#333", relief="flat", anchor="w", padx=20, pady=8,
                            command=lambda c=cat: self.switch_category(c))
            btn.pack(fill=tk.X, pady=1)
            self.cat_buttons[cat] = btn
        self.highlight_category()

        # 2. CỘT GIỮA: LƯỚI SẢN PHẨM
        center_panel = tk.Frame(main_container, bg="#f0f2f5")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas cuộn
        self.canvas = tk.Canvas(center_panel, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(center_panel, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg="#f0f2f5")

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.render_products()

        # 3. CỘT PHẢI: GIỎ HÀNG & THANH TOÁN
        cart_panel = tk.Frame(main_container, bg="white", width=320)
        cart_panel.pack(side=tk.RIGHT, fill=tk.Y)
        cart_panel.pack_propagate(False)

        tk.Label(cart_panel, text="GIỎ HÀNG", font=("Arial", 14, "bold"), bg="white", fg="#0f1746").pack(pady=20)

        # List các món đã chọn (Listbox hoặc Frame cuộn)
        self.cart_list_frame = tk.Frame(cart_panel, bg="white")
        self.cart_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Phần Tổng tiền & Nút
        footer = tk.Frame(cart_panel, bg="#f9f9f9", padx=15, pady=20)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_total = tk.Label(footer, text="Tổng tiền: 0 VND", font=("Arial", 14, "bold"), bg="#f9f9f9",
                                  fg="#d32f2f")
        self.lbl_total.pack(pady=10)

        tk.Button(footer, text="THANH TOÁN", bg="#ff9800", fg="white", font=("Arial", 12, "bold"),
                  height=2, relief="flat", width=20, command=self.on_payment).pack()

        self.update_cart_ui()

    # --- LOGIC HIỂN THỊ SẢN PHẨM ---
    def switch_category(self, category):
        self.current_category = category
        self.highlight_category()
        self.render_products()

    def highlight_category(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.current_category:
                btn.config(bg="#1976d2", fg="white", font=("Arial", 10, "bold"))
            else:
                btn.config(bg="white", fg="#333", font=("Arial", 10, "normal"))

    def render_products(self):
        for w in self.grid_frame.winfo_children(): w.destroy()

        display_products = self.all_products if self.current_category == "Tất cả" else [p for p in self.all_products if
                                                                                        p.category == self.current_category]

        COLUMNS = 3
        for idx, p in enumerate(display_products):
            self.create_card(p, idx // COLUMNS, idx % COLUMNS)

    def create_card(self, product, row, col):
        card = tk.Frame(self.grid_frame, bg="white", bd=1, relief="solid")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        self.grid_frame.grid_columnconfigure(col, weight=1)

        # Ảnh
        img_h = 100
        if product.image_path and os.path.exists(product.image_path):
            try:
                img = Image.open(product.image_path)
                img = img.resize((100, img_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                l = tk.Label(card, image=photo, bg="white")
                l.image = photo
                l.pack(pady=5)
            except:
                tk.Label(card, text="IMG", height=5, bg="#eee").pack(fill=tk.X)
        else:
            tk.Label(card, text="IMG", height=5, bg="#eee").pack(fill=tk.X)

        tk.Label(card, text=product.name, font=("Arial", 10, "bold"), bg="white", wraplength=120).pack()
        tk.Label(card, text=f"{int(product.price):,} đ", fg="#e65100", bg="white").pack()

        btn = tk.Button(card, text="Thêm", bg="#5c6bc0", fg="white", font=("Arial", 9), relief="flat",
                        command=lambda: self.add_to_cart(product))
        btn.pack(pady=5, ipadx=10)

    # --- LOGIC GIỎ HÀNG ---
    def add_to_cart(self, product):
        pid = product.product_id
        if pid in self.cart:
            self.cart[pid]['qty'] += 1
        else:
            self.cart[pid] = {'obj': product, 'qty': 1}
        self.update_cart_ui()

    def remove_one(self, pid):
        if pid in self.cart:
            self.cart[pid]['qty'] -= 1
            if self.cart[pid]['qty'] <= 0:
                del self.cart[pid]
            self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_list_frame.winfo_children(): w.destroy()

        total = 0
        for pid, item in self.cart.items():
            p = item['obj']
            qty = item['qty']
            cost = p.price * qty
            total += cost

            # Row trong giỏ hàng
            row = tk.Frame(self.cart_list_frame, bg="white", pady=5)
            row.pack(fill=tk.X, anchor="n")

            tk.Label(row, text=f"{p.name}", bg="white", width=15, anchor="w", font=("Arial", 10)).pack(side=tk.LEFT)
            tk.Label(row, text=f"x{qty}", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=f"{int(cost):,} đ", bg="white", fg="#333").pack(side=tk.RIGHT)

            tk.Button(row, text="-", width=2, bg="#eee", relief="flat",
                      command=lambda i=pid: self.remove_one(i)).pack(side=tk.RIGHT, padx=5)

        self.lbl_total.config(text=f"Tổng tiền: {int(total):,} VND")
        self.current_total = total

    def on_payment(self):
        if not self.cart:
            messagebox.showwarning("Trống", "Vui lòng chọn sản phẩm!")
            return

        if messagebox.askyesno("Thanh toán", f"Xác nhận thanh toán hóa đơn {int(self.current_total):,} VND?"):
            # Chuẩn bị dữ liệu
            products_list = []
            for pid, item in self.cart.items():
                products_list.append((pid, item['qty'], item['obj'].price))

            # Gọi Controller
            success, msg = self.controller.process_direct_sale(self.user_id, self.current_total, products_list)

            if success:
                messagebox.showinfo("Thành công", msg)
                self.cart = {}  # Reset giỏ hàng
                self.update_cart_ui()
            else:
                messagebox.showerror("Lỗi", msg)