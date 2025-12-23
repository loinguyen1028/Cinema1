import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from controllers.product_controller import ProductController
from controllers.customer_controller import CustomerController
from controllers.ticket_controller import TicketController
from views.payment_dialog import PaymentConfirmDialog
from datetime import datetime
from utils.ticket_printer import print_ticket_pdf

class ConcessionSales:
    def __init__(self, parent_frame, user_id):
        self.parent = parent_frame
        self.user_id = user_id
        self.controller = ProductController()
        self.cust_controller = CustomerController()  # Thêm controller khách hàng

        # Giỏ hàng: {product_id: {'obj': product, 'qty': 1}}
        self.cart = {}

        # Biến logic giảm giá
        self.current_customer = None
        self.discount_percent = 0.0
        self.subtotal = 0
        self.final_total = 0

        # Lấy dữ liệu
        self.all_products = self.controller.get_all()
        categories_set = set(p.category for p in self.all_products if p.category)
        self.categories = ["Tất cả"] + sorted(list(categories_set))
        self.current_category = "Tất cả"

        self.render()

    def render(self):
        # Container chính
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
        cart_panel = tk.Frame(main_container, bg="white", width=350)  # Tăng width lên xíu
        cart_panel.pack(side=tk.RIGHT, fill=tk.Y)
        cart_panel.pack_propagate(False)

        tk.Label(cart_panel, text="ĐƠN HÀNG", font=("Arial", 14, "bold"), bg="white", fg="#0f1746").pack(pady=(20, 10))

        # --- MỚI: KHU VỰC KHÁCH HÀNG ---
        cust_frame = tk.LabelFrame(cart_panel, text="Khách hàng & Ưu đãi", bg="white", font=("Arial", 10, "bold"))
        cust_frame.pack(fill=tk.X, padx=10, pady=5)

        # Chọn loại khách
        self.cbo_cust_type = ttk.Combobox(cust_frame, values=["Khách vãng lai", "Sinh viên (Giảm 20%)", "Thành viên"],
                                          state="readonly")
        self.cbo_cust_type.current(0)
        self.cbo_cust_type.pack(fill=tk.X, padx=5, pady=5)
        self.cbo_cust_type.bind("<<ComboboxSelected>>", self.on_cust_type_change)

        # Nhập SĐT (Mặc định ẩn/disable)
        f_phone = tk.Frame(cust_frame, bg="white")
        f_phone.pack(fill=tk.X, padx=5, pady=5)

        self.e_phone = tk.Entry(f_phone, font=("Arial", 11), bg="#f5f5f5", state="disabled")
        self.e_phone.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.e_phone.bind("<Return>", lambda e: self.check_member())

        self.btn_check = tk.Button(f_phone, text="🔎", bg="#eee", command=self.check_member, state="disabled")
        self.btn_check.pack(side=tk.RIGHT, padx=(5, 0))

        self.lbl_cust_info = tk.Label(cust_frame, text="", bg="white", fg="green", font=("Arial", 9, "italic"))
        self.lbl_cust_info.pack(anchor="w", padx=5, pady=(0, 5))
        # -------------------------------

        # List các món (Frame cuộn)
        list_container = tk.Frame(cart_panel, bg="white")
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Header cho list
        h_frame = tk.Frame(list_container, bg="#eee")
        h_frame.pack(fill=tk.X)
        tk.Label(h_frame, text="Món", bg="#eee", width=20, anchor="w").pack(side=tk.LEFT)
        tk.Label(h_frame, text="SL", bg="#eee", width=5).pack(side=tk.LEFT)
        tk.Label(h_frame, text="Thành tiền", bg="#eee").pack(side=tk.RIGHT)

        self.cart_list_frame = tk.Frame(list_container, bg="white")
        self.cart_list_frame.pack(fill=tk.BOTH, expand=True)

        # Footer Tổng tiền
        footer = tk.Frame(cart_panel, bg="#f9f9f9", padx=15, pady=20)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_subtotal = tk.Label(footer, text="Tạm tính: 0", font=("Arial", 10), bg="#f9f9f9", anchor="e")
        self.lbl_subtotal.pack(fill=tk.X)

        self.lbl_discount = tk.Label(footer, text="Giảm giá: 0", font=("Arial", 10), bg="#f9f9f9", fg="red", anchor="e")
        self.lbl_discount.pack(fill=tk.X)

        tk.Frame(footer, height=1, bg="#ddd").pack(fill=tk.X, pady=5)

        self.lbl_total = tk.Label(footer, text="0 VND", font=("Arial", 16, "bold"), bg="#f9f9f9", fg="#d32f2f",
                                  anchor="e")
        self.lbl_total.pack(pady=(0, 10), fill=tk.X)

        tk.Button(footer, text="THANH TOÁN", bg="#ff9800", fg="white", font=("Arial", 12, "bold"),
                  height=2, relief="flat", width=20, command=self.on_payment_click).pack()

        self.update_cart_ui()

    # --- LOGIC SẢN PHẨM (Giữ nguyên) ---
    def switch_category(self, category):
        self.current_category = category
        self.highlight_category()
        self.render_products()

    def highlight_category(self):
        for cat, btn in self.cat_buttons.items():
            btn.config(bg="#1976d2" if cat == self.current_category else "white",
                       fg="white" if cat == self.current_category else "#333",
                       font=("Arial", 10, "bold") if cat == self.current_category else ("Arial", 10))

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

        # Xử lý ảnh
        img_h = 100
        try:
            if product.image_path and os.path.exists(product.image_path):
                img = Image.open(product.image_path).resize((100, img_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                l = tk.Label(card, image=photo, bg="white")
                l.image = photo
                l.pack(pady=5)
            else:
                tk.Label(card, text="NO IMAGE", height=5, bg="#eee", fg="#999").pack(fill=tk.X)
        except:
            tk.Label(card, text="ERROR", height=5, bg="#eee").pack(fill=tk.X)

        tk.Label(card, text=product.name, font=("Arial", 10, "bold"), bg="white", wraplength=120).pack()
        tk.Label(card, text=f"{int(product.price):,} đ", fg="#e65100", bg="white").pack()

        tk.Button(card, text="Thêm", bg="#5c6bc0", fg="white", font=("Arial", 9), relief="flat",
                  command=lambda: self.add_to_cart(product)).pack(pady=5, ipadx=10)

    # --- LOGIC KHÁCH HÀNG & GIẢM GIÁ ---
    def on_cust_type_change(self, event):
        selection = self.cbo_cust_type.get()
        # Reset
        self.current_customer = None
        self.e_phone.delete(0, tk.END)
        self.lbl_cust_info.config(text="")

        if "Sinh viên" in selection:
            self.discount_percent = 0.20
            self.e_phone.config(state="disabled", bg="#f5f5f5")
            self.btn_check.config(state="disabled", bg="#eee")
        elif "Thành viên" in selection:
            self.discount_percent = 0.0  # Chờ check
            self.e_phone.config(state="normal", bg="white")
            self.btn_check.config(state="normal", bg="#5c6bc0", fg="white")
            self.e_phone.focus()
        else:  # Khách vãng lai
            self.discount_percent = 0.0
            self.e_phone.config(state="disabled", bg="#f5f5f5")
            self.btn_check.config(state="disabled", bg="#eee")

        self.update_cart_ui()

    def check_member(self):
        phone = self.e_phone.get().strip()
        if not phone: return

        cus = self.cust_controller.get_by_phone(phone)

        if cus:
            self.current_customer = cus

            # --- CODE MỚI: Lấy thông tin từ quan hệ bảng tier ---
            if cus.tier:
                level_name = cus.tier.tier_name
                # Database lưu số nguyên (ví dụ 10 nghĩa là 10%) -> chia 100
                # Hoặc nếu lưu 0.1 thì không cần chia.
                # Ở các bước trước bạn lưu 5, 10 -> nên chia 100.
                self.discount_percent = float(cus.tier.discount_percent) / 100
            else:
                level_name = "Chưa xếp hạng"
                self.discount_percent = 0.0
            # ----------------------------------------------------

            # Hiển thị
            discount_display = int(self.discount_percent * 100)
            self.lbl_cust_info.config(
                text=f"{cus.name} - {level_name} (-{discount_display}%)",
                fg="green"
            )
        else:
            self.discount_percent = 0.0
            self.lbl_cust_info.config(text="Không tìm thấy khách hàng!", fg="red")

        self.update_cart_ui()

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
        # 1. Xóa danh sách hiển thị cũ để vẽ lại
        for w in self.cart_list_frame.winfo_children(): w.destroy()

        subtotal = 0.0  # Khởi tạo là float

        # 2. Duyệt qua giỏ hàng
        for pid, item in self.cart.items():
            p = item['obj']
            qty = item['qty']

            # --- QUAN TRỌNG: Ép kiểu Decimal -> float để tránh lỗi TypeError ---
            price_val = float(p.price)
            cost = price_val * qty

            subtotal += cost

            # 3. Vẽ dòng sản phẩm (Row)
            row = tk.Frame(self.cart_list_frame, bg="white", pady=2)
            row.pack(fill=tk.X)

            # Tên món
            tk.Label(row, text=p.name, bg="white", width=20, anchor="w", font=("Arial", 9)).pack(side=tk.LEFT)
            # Số lượng
            tk.Label(row, text=f"x{qty}", bg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT)

            # Nút xóa nhỏ [-]
            btn_del = tk.Label(row, text="[-]", fg="red", bg="white", cursor="hand2")
            btn_del.pack(side=tk.RIGHT, padx=5)
            btn_del.bind("<Button-1>", lambda e, i=pid: self.remove_one(i))

            # Thành tiền món đó
            tk.Label(row, text=f"{int(cost):,}", bg="white", fg="#333", width=10, anchor="e").pack(side=tk.RIGHT)

        # 4. Tính toán tổng cộng & Giảm giá
        self.subtotal = subtotal

        # Vì subtotal đã là float nên nhân với discount_percent (float) sẽ không lỗi
        discount_amt = subtotal * self.discount_percent
        self.final_total = subtotal - discount_amt

        # 5. Cập nhật các Label dưới chân trang
        self.lbl_subtotal.config(text=f"Tạm tính: {int(subtotal):,} đ")

        if discount_amt > 0:
            self.lbl_discount.config(text=f"Giảm giá: -{int(discount_amt):,} đ")
        else:
            self.lbl_discount.config(text="")

        self.lbl_total.config(text=f"{int(self.final_total):,} VND")

    # --- THANH TOÁN ---
    def on_payment_click(self):
        if not self.cart:
            messagebox.showwarning("Trống", "Vui lòng chọn sản phẩm!")
            return

        # Callback xử lý lưu DB sau khi đã nhập tiền xong
        def save_transaction():
            # Chuẩn bị list sản phẩm để lưu
            products_list = []
            for pid, item in self.cart.items():
                products_list.append((pid, item['qty'], item['obj'].price))

            # Khách hàng ID (nếu có)
            cus_id = self.current_customer.customer_id if self.current_customer else None

            # Gọi Controller xử lý lưu
            # Lưu ý: Bạn cần đảm bảo ProductController có hàm 'process_direct_sale'
            # Hàm này sẽ gọi DAO insert vào ticket (loại bán lẻ) hoặc bảng sales riêng
            success, msg = self.controller.process_direct_sale(self.user_id, self.final_total, products_list, cus_id)

            if success:
                messagebox.showinfo("Thành công", msg)

                # --- ĐOẠN CODE MỚI ĐỂ IN HÓA ĐƠN ---
                try:
                    # 1. Lấy mã hóa đơn (msg trả về "Thanh toán thành công! Mã vé: 123")
                    import re
                    ticket_id = "UNKNOWN"
                    match = re.search(r"Mã vé:\s*(\d+)", msg)
                    if match: ticket_id = match.group(1)

                    # 2. Tạo chuỗi món ăn (ngang, cách nhau dấu phẩy)
                    items_str = []
                    for pid, item in self.cart.items():
                        items_str.append(f"{item['qty']}x {item['obj'].name}")
                    food_str = ", ".join(items_str)

                    # 3. Lấy tên nhân viên
                    # Mẹo: Dùng tạm TicketController để tra tên user
                    tc = TicketController()
                    seller_name = tc.get_user_name(self.user_id)

                    # 4. Đóng gói dữ liệu in
                    # QUAN TRỌNG: Không truyền 'movie_name' để máy in biết đây là hóa đơn lẻ
                    bill_data = {
                        "ticket_id": ticket_id,
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "time": datetime.now().strftime("%H:%M"),
                        "price": int(self.final_total),
                        "seller": seller_name,
                        "food": food_str,
                        "movie_name": None  # <--- Đánh dấu là không có phim
                    }

                    # 5. Gọi in
                    print_ticket_pdf(bill_data)

                except Exception as e:
                    print(f"Lỗi in hóa đơn: {e}")
                # -----------------------------------

                self.cart = {}  # Reset
                self.on_cust_type_change(None)
                self.update_cart_ui()
            else:
                messagebox.showerror("Lỗi", msg)

        # Mở Dialog xác thực thanh toán
        PaymentConfirmDialog(self.parent, self.final_total, on_confirm=save_transaction)