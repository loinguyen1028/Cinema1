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
        self.cust_controller = CustomerController()

        # THEME CINEMA (UI ONLY)
        self.colors = {
            "bg_main": "#121212",
            "bg_panel": "#1c1c1c",
            "bg_card": "#222222",
            "text_main": "#ffffff",
            "text_muted": "#aaaaaa",
            "accent": "#f5c518",
            "danger": "#e53935",
            "success": "#4caf50",
            "border": "#333333"
        }

        self.cart = {}
        self.current_customer = None
        self.discount_percent = 0.0
        self.subtotal = 0
        self.final_total = 0

        self.all_products = self.controller.get_all()
        categories_set = set(p.category for p in self.all_products if p.category)
        self.categories = ["Tất cả"] + sorted(list(categories_set))
        self.current_category = "Tất cả"

        self.render()

    # ================= RENDER =================
    def render(self):
        main_container = tk.Frame(self.parent, bg=self.colors["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # ===== LEFT: CATEGORY =====
        cat_panel = tk.Frame(main_container, bg=self.colors["bg_panel"], width=200)
        cat_panel.pack(side=tk.LEFT, fill=tk.Y)
        cat_panel.pack_propagate(False)

        tk.Label(
            cat_panel, text="DANH MỤC",
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            font=("Arial", 11, "bold")
        ).pack(pady=20)

        self.cat_buttons = {}
        for cat in self.categories:
            btn = tk.Button(
                cat_panel, text=cat,
                bg=self.colors["bg_panel"],
                fg=self.colors["text_main"],
                font=("Arial", 10),
                relief="flat",
                anchor="w",
                padx=20, pady=10,
                command=lambda c=cat: self.switch_category(c)
            )
            btn.pack(fill=tk.X)
            self.cat_buttons[cat] = btn
        self.highlight_category()

        # ===== CENTER: PRODUCTS =====
        center_panel = tk.Frame(main_container, bg=self.colors["bg_main"])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(center_panel, bg=self.colors["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(center_panel, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=self.colors["bg_main"])

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.render_products()

        # ===== RIGHT: CART =====
        cart_panel = tk.Frame(main_container, bg=self.colors["bg_panel"], width=360)
        cart_panel.pack(side=tk.RIGHT, fill=tk.Y)
        cart_panel.pack_propagate(False)

        tk.Label(
            cart_panel, text="ĐƠN HÀNG",
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            font=("Arial", 15, "bold")
        ).pack(pady=(20, 10))

        # ---- CUSTOMER ----
        cust_frame = tk.LabelFrame(
            cart_panel, text=" Khách hàng & Ưu đãi ",
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            font=("Arial", 10, "bold")
        )
        cust_frame.pack(fill=tk.X, padx=10, pady=5)

        self.cbo_cust_type = ttk.Combobox(
            cust_frame,
            values=["Khách vãng lai", "Sinh viên (Giảm 20%)", "Thành viên"],
            state="readonly"
        )
        self.cbo_cust_type.current(0)
        self.cbo_cust_type.pack(fill=tk.X, padx=5, pady=5)
        self.cbo_cust_type.bind("<<ComboboxSelected>>", self.on_cust_type_change)

        f_phone = tk.Frame(cust_frame, bg=self.colors["bg_panel"])
        f_phone.pack(fill=tk.X, padx=5, pady=5)

        self.e_phone = tk.Entry(f_phone, font=("Arial", 11), state="disabled")
        self.e_phone.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.e_phone.bind("<Return>", lambda e: self.check_member())

        self.btn_check = tk.Button(
            f_phone, text="🔎", state="disabled",
            bg=self.colors["border"], fg="white",
            command=self.check_member
        )
        self.btn_check.pack(side=tk.RIGHT, padx=(5, 0))

        self.lbl_cust_info = tk.Label(
            cust_frame, text="",
            bg=self.colors["bg_panel"],
            fg=self.colors["success"],
            font=("Arial", 9, "italic")
        )
        self.lbl_cust_info.pack(anchor="w", padx=5, pady=(0, 5))

        # ---- CART LIST ----
        list_container = tk.Frame(cart_panel, bg=self.colors["bg_panel"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.cart_list_frame = tk.Frame(list_container, bg=self.colors["bg_panel"])
        self.cart_list_frame.pack(fill=tk.BOTH, expand=True)

        # ---- FOOTER ----
        footer = tk.Frame(cart_panel, bg=self.colors["bg_panel"], padx=15, pady=20)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_subtotal = tk.Label(footer, bg=self.colors["bg_panel"], fg=self.colors["text_main"])
        self.lbl_subtotal.pack(fill=tk.X)

        self.lbl_discount = tk.Label(footer, bg=self.colors["bg_panel"], fg=self.colors["danger"])
        self.lbl_discount.pack(fill=tk.X)

        self.lbl_total = tk.Label(
            footer, text="0 VND",
            bg=self.colors["bg_panel"],
            fg=self.colors["accent"],
            font=("Arial", 18, "bold"),
            anchor="e"
        )
        self.lbl_total.pack(pady=(10, 10), fill=tk.X)

        tk.Button(
            footer, text="💳 THANH TOÁN",
            bg=self.colors["accent"],
            fg="#000",
            font=("Arial", 13, "bold"),
            height=2,
            relief="flat",
            command=self.on_payment_click
        ).pack(fill=tk.X)

        self.update_cart_ui()

    # ================= PRODUCTS =================
    def switch_category(self, category):
        self.current_category = category
        self.highlight_category()
        self.render_products()

    def highlight_category(self):
        for cat, btn in self.cat_buttons.items():
            btn.config(
                bg=self.colors["accent"] if cat == self.current_category else self.colors["bg_panel"],
                fg="#000" if cat == self.current_category else self.colors["text_main"],
                font=("Arial", 10, "bold") if cat == self.current_category else ("Arial", 10)
            )

    def render_products(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        products = self.all_products if self.current_category == "Tất cả" else [
            p for p in self.all_products if p.category == self.current_category
        ]

        for idx, p in enumerate(products):
            self.create_card(p, idx // 3, idx % 3)

    def create_card(self, product, row, col):
        card = tk.Frame(self.grid_frame, bg=self.colors["bg_card"], bd=1, relief="solid")
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        try:
            if product.image_path and os.path.exists(product.image_path):
                img = Image.open(product.image_path).resize((120, 120))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(card, image=photo, bg=self.colors["bg_card"])
                lbl.image = photo
                lbl.pack(pady=5)
        except:
            pass

        tk.Label(card, text=product.name, bg=self.colors["bg_card"],
                 fg=self.colors["text_main"], wraplength=140).pack()

        tk.Label(card, text=f"{int(product.price):,} đ",
                 fg=self.colors["accent"], bg=self.colors["bg_card"],
                 font=("Arial", 10, "bold")).pack()

        tk.Button(
            card, text="➕ Thêm",
            bg=self.colors["accent"], fg="#000",
            relief="flat",
            command=lambda: self.add_to_cart(product)
        ).pack(pady=6, ipadx=15)

    # ================= CART =================
    def add_to_cart(self, product):
        pid = product.product_id
        self.cart.setdefault(pid, {"obj": product, "qty": 0})
        self.cart[pid]["qty"] += 1
        self.update_cart_ui()

    def remove_one(self, pid):
        if pid in self.cart:
            self.cart[pid]["qty"] -= 1
            if self.cart[pid]["qty"] <= 0:
                del self.cart[pid]
        self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_list_frame.winfo_children():
            w.destroy()

        subtotal = 0.0
        for pid, item in self.cart.items():
            p = item["obj"]
            qty = item["qty"]
            cost = float(p.price) * qty
            subtotal += cost

            row = tk.Frame(self.cart_list_frame, bg=self.colors["bg_panel"])
            row.pack(fill=tk.X, pady=3)

            tk.Label(row, text=p.name, bg=self.colors["bg_panel"],
                     fg=self.colors["text_main"], width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=f"x{qty}", bg=self.colors["bg_panel"],
                     fg=self.colors["accent"]).pack(side=tk.LEFT)

            btn = tk.Label(row, text="✖", fg=self.colors["danger"],
                           bg=self.colors["bg_panel"], cursor="hand2")
            btn.pack(side=tk.RIGHT)
            btn.bind("<Button-1>", lambda e, i=pid: self.remove_one(i))

            tk.Label(row, text=f"{int(cost):,}",
                     bg=self.colors["bg_panel"], fg=self.colors["text_main"]).pack(side=tk.RIGHT)

        self.subtotal = subtotal
        discount_amt = subtotal * self.discount_percent
        self.final_total = subtotal - discount_amt

        self.lbl_subtotal.config(text=f"Tạm tính: {int(subtotal):,} đ")
        self.lbl_discount.config(text=f"Giảm giá: -{int(discount_amt):,} đ" if discount_amt > 0 else "")
        self.lbl_total.config(text=f"{int(self.final_total):,} VND")

    # ================= CUSTOMER =================
    def on_cust_type_change(self, event):
        self.current_customer = None
        self.discount_percent = 0.0
        self.lbl_cust_info.config(text="")

        sel = self.cbo_cust_type.get()
        if "Sinh viên" in sel:
            self.discount_percent = 0.2
            self.e_phone.config(state="disabled")
            self.btn_check.config(state="disabled")
        elif "Thành viên" in sel:
            self.e_phone.config(state="normal")
            self.btn_check.config(state="normal")
        else:
            self.e_phone.config(state="disabled")
            self.btn_check.config(state="disabled")

        self.update_cart_ui()

    def check_member(self):
        phone = self.e_phone.get().strip()
        if not phone:
            return

        cus = self.cust_controller.get_by_phone(phone)
        if cus:
            self.current_customer = cus
            if cus.tier:
                self.discount_percent = float(cus.tier.discount_percent) / 100
                self.lbl_cust_info.config(
                    text=f"{cus.name} - {cus.tier.tier_name} (-{int(self.discount_percent*100)}%)",
                    fg=self.colors["success"]
                )
        else:
            self.lbl_cust_info.config(text="Không tìm thấy khách hàng!", fg=self.colors["danger"])

        self.update_cart_ui()

    # ================= PAYMENT =================
    def on_payment_click(self):
        if not self.cart:
            messagebox.showwarning("Trống", "Vui lòng chọn sản phẩm!")
            return

        def save_transaction():
            products_list = [(pid, i["qty"], i["obj"].price) for pid, i in self.cart.items()]
            cus_id = self.current_customer.customer_id if self.current_customer else None

            success, msg = self.controller.process_direct_sale(
                self.user_id, self.final_total, products_list, cus_id
            )

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

        PaymentConfirmDialog(self.parent, self.final_total, on_confirm=save_transaction)
