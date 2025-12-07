import tkinter as tk
from tkinter import ttk, messagebox
from dao.seat_dao import SeatDAO
from views.concession_dialog import ConcessionDialog  # <--- Import dialog chọn món
from views.payment_dialog import PaymentConfirmDialog

class BookingDialog(tk.Toplevel):
    def __init__(self, parent, controller, st_id, current_user_id):
        super().__init__(parent)
        self.controller = controller
        self.st_id = st_id
        self.user_id = current_user_id  # ID nhân viên bán vé
        self.seat_dao = SeatDAO()

        self.title("Bán vé & Thanh toán")
        self.geometry("1250x750")
        self.config(bg="#f0f2f5")
        self.grab_set()

        # Dữ liệu suất chiếu
        self.st = self.controller.get_detail(st_id)

        # Biến trạng thái
        self.selected_seats = set()  # Set chứa ID các ghế đang chọn
        self.seat_objects = {}  # Map để quản lý giao diện ghế

        # Biến tính toán & Giỏ hàng
        self.current_customer = None
        self.member_discount_percent = 0.0
        self.special_discount_percent = 0.0
        self.final_total_amount = 0
        self.selected_products = {}  # {product_id: {'obj': product, 'qty': 1}}

        if not self.st:
            self.destroy()
            return

        self.render_ui()

    def render_ui(self):
        # ====================================================
        # PANEL TRÁI: THÔNG TIN - ƯU ĐÃI - BẮP NƯỚC - THANH TOÁN
        # ====================================================
        left_panel = tk.Frame(self, bg="white", width=350, relief="solid", bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # 1. Header Phim
        tk.Label(left_panel, text=self.st.movie.title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#0f1746", wraplength=300).pack(pady=(30, 10), padx=20)

        # 2. Thông tin suất chiếu
        info_frame = tk.Frame(left_panel, bg="#f9f9f9", padx=15, pady=15)
        info_frame.pack(fill=tk.X, padx=20)

        def add_line(lbl, val):
            r = tk.Frame(info_frame, bg="#f9f9f9")
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=lbl, font=("Arial", 10, "bold"), bg="#f9f9f9", fg="#555").pack(side=tk.LEFT)
            tk.Label(r, text=val, font=("Arial", 10), bg="#f9f9f9", fg="#333").pack(side=tk.RIGHT)

        add_line("Rạp:", self.st.room.room_name)
        add_line("Ngày:", self.st.start_time.strftime("%d/%m/%Y"))
        add_line("Suất:", self.st.start_time.strftime("%H:%M"))
        add_line("Giá vé:", f"{int(self.st.ticket_price):,} đ")

        tk.Label(left_panel, text="--------------------", bg="white", fg="#ddd").pack(pady=5)

        # 3. Khu vực Ưu đãi & Thành viên
        promo_frame = tk.LabelFrame(left_panel, text="Ưu đãi & Thành viên", bg="white", font=("Arial", 10, "bold"),
                                    fg="#333")
        promo_frame.pack(fill=tk.X, padx=20, pady=5)

        # Chọn đối tượng
        f_type = tk.Frame(promo_frame, bg="white")
        f_type.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(f_type, text="Đối tượng:", bg="white", fg="#555").pack(side=tk.LEFT)
        self.cbo_type = ttk.Combobox(f_type, values=["Người lớn / Thành viên", "Sinh viên", "Trẻ em"],
                                     font=("Arial", 10), state="readonly", width=18)
        self.cbo_type.current(0)
        self.cbo_type.pack(side=tk.RIGHT)
        self.cbo_type.bind("<<ComboboxSelected>>", self.on_type_change)

        # Nhập SĐT
        self.f_phone = tk.Frame(promo_frame, bg="white")
        self.f_phone.pack(fill=tk.X, padx=10, pady=5)
        self.e_phone = tk.Entry(self.f_phone, font=("Arial", 11), width=15, relief="solid", bd=1)
        self.e_phone.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.e_phone.insert(0, "")
        self.e_phone.bind("<Return>", lambda e: self.check_member())

        self.btn_check = tk.Button(self.f_phone, text="Kiểm tra", bg="#5c6bc0", fg="white", font=("Arial", 9),
                                   relief="flat", command=self.check_member)
        self.btn_check.pack(side=tk.RIGHT, padx=5)

        self.lbl_member_info = tk.Label(promo_frame, text="Khách vãng lai (Không giảm)",
                                        bg="white", fg="#666", font=("Arial", 9, "italic"), wraplength=300)
        self.lbl_member_info.pack(anchor="w", padx=10, pady=(0, 10))

        # 4. Khu vực Bắp Nước
        f_food = tk.LabelFrame(left_panel, text="Bắp & Nước", bg="white", font=("Arial", 10, "bold"), fg="#333")
        f_food.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(f_food, text="🍿 Chọn món", bg="#8d6e63", fg="white", font=("Arial", 9),
                  relief="flat", command=self.open_concession_dialog).pack(side=tk.RIGHT, padx=10, pady=10)

        self.lbl_food_list = tk.Label(f_food, text="Chưa chọn món", bg="white", fg="#555", font=("Arial", 9),
                                      wraplength=200, justify="left")
        self.lbl_food_list.pack(side=tk.LEFT, padx=10, pady=10, anchor="w")

        # 5. Khu vực Tính tiền
        tk.Label(left_panel, text="THANH TOÁN", font=("Arial", 11, "bold"), bg="white", fg="#333").pack(pady=(15, 5))

        self.lbl_seat_list = tk.Label(left_panel, text="Ghế: -", font=("Arial", 10), bg="white", fg="#ff9800",
                                      wraplength=300)
        self.lbl_seat_list.pack(pady=2)

        self.lbl_subtotal = tk.Label(left_panel, text="", font=("Arial", 10), bg="white", fg="#555")
        self.lbl_subtotal.pack()

        self.lbl_discount = tk.Label(left_panel, text="", font=("Arial", 10), bg="white", fg="green")
        self.lbl_discount.pack()

        self.lbl_total = tk.Label(left_panel, text="TỔNG: 0 VND", font=("Arial", 16, "bold"), bg="white", fg="#d32f2f")
        self.lbl_total.pack(pady=10)

        # Footer Buttons
        btn_frame = tk.Frame(left_panel, bg="white")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=30, padx=20)
        tk.Button(btn_frame, text="Hủy", bg="#eee", width=10, relief="flat", command=self.destroy).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="THANH TOÁN", bg="#ff9800", fg="white", font=("Arial", 11, "bold"),
                  width=15, relief="flat", command=self.on_payment).pack(side=tk.RIGHT)

        # ====================================================
        # PANEL PHẢI: SƠ ĐỒ GHẾ
        # ====================================================
        right_panel = tk.Frame(self, bg="#f0f2f5")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        legend = tk.Frame(right_panel, bg="#f0f2f5", pady=15)
        legend.pack(fill=tk.X, padx=20)
        tk.Label(legend, text="Sơ đồ ghế", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        # Chú thích màu
        def add_legend(color, text, text_col="black"):
            f = tk.Frame(legend, bg="#f0f2f5")
            f.pack(side=tk.LEFT, padx=10)
            tk.Label(f, bg=color, width=3, height=1, relief="solid", bd=1).pack(side=tk.LEFT)
            tk.Label(f, text=text, bg="#f0f2f5", fg=text_col, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        add_legend("white", "Trống", "#2e7d32")
        add_legend("#555", "Đã bán", "#555")
        add_legend("#ff9800", "Đang chọn")

        self.canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        self.load_seat_map()

    # ---------------------------------------------------------
    # LOGIC VẼ SƠ ĐỒ GHẾ
    # ---------------------------------------------------------
    def load_seat_map(self):
        all_seats = self.seat_dao.get_seats_by_room(self.st.room_id)
        booked_ids = self.seat_dao.get_booked_seat_ids(self.st.showtime_id)
        self.draw_interactive_map(all_seats, booked_ids)

    def draw_interactive_map(self, all_seats, booked_ids):
        rows_map = {}
        for s in all_seats:
            if s.seat_row not in rows_map: rows_map[s.seat_row] = []
            rows_map[s.seat_row].append(s)
        sorted_rows = sorted(rows_map.keys())

        SEAT_W, SEAT_H = 36, 30
        GAP_X, GAP_Y = 6, 10
        START_Y = 100

        max_cols = max(len(r) for r in rows_map.values()) if rows_map else 0
        total_width = max_cols * (SEAT_W + GAP_X)
        canvas_width = 850
        start_x = max(20, (canvas_width - total_width) // 2)

        # Màn hình
        screen_w = total_width + 100
        screen_x = start_x - 50
        self.canvas.create_arc(screen_x, 20, screen_x + screen_w, 80, start=0, extent=-180, style=tk.ARC, width=3,
                               outline="#999")
        self.canvas.create_text(screen_x + screen_w / 2, 60, text="MÀN HÌNH", font=("Arial", 10, "bold"), fill="#999")

        y = START_Y
        self.seat_objects = {}
        for r_name in sorted_rows:
            seats = sorted(rows_map[r_name], key=lambda x: x.seat_number)
            row_w = len(seats) * (SEAT_W + GAP_X)
            x = start_x + (total_width - row_w) // 2
            for s in seats:
                is_booked = s.seat_id in booked_ids
                fill_color = "#555" if is_booked else "white"
                text_color = "white" if is_booked else "#2e7d32"
                outline = "#555" if is_booked else "#2e7d32"
                tags = ("seat", f"seat_{s.seat_id}")

                rect = self.canvas.create_rectangle(x, y, x + SEAT_W, y + SEAT_H, fill=fill_color, outline=outline,
                                                    width=1.5, tags=tags)
                lbl = f"{s.seat_row}{s.seat_number}"
                text = self.canvas.create_text(x + SEAT_W / 2, y + SEAT_H / 2, text=lbl, font=("Arial", 8, "bold"),
                                               fill=text_color, tags=tags)

                if not is_booked:
                    self.seat_objects[rect] = {'id': s.seat_id, 'lbl': lbl, 'text_item': text, 'selected': False}
                    self.seat_objects[text] = {'parent': rect}
                    self.canvas.tag_bind(rect, "<Button-1>", lambda e, r=rect: self.toggle_seat(r))
                    self.canvas.tag_bind(text, "<Button-1>", lambda e, r=rect: self.toggle_seat(r))
                x += SEAT_W + GAP_X
            y += SEAT_H + GAP_Y
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_seat(self, rect_item):
        if rect_item not in self.seat_objects:
            parent = self.seat_objects.get(rect_item, {}).get('parent')
            if parent:
                rect_item = parent
            else:
                return

        data = self.seat_objects.get(rect_item)
        if not data: return

        seat_id = data['id']
        text_item = data['text_item']

        if data['selected']:
            self.canvas.itemconfig(rect_item, fill="white", outline="#2e7d32")
            self.canvas.itemconfig(text_item, fill="#2e7d32")
            self.selected_seats.remove(seat_id)
            data['selected'] = False
        else:
            self.canvas.itemconfig(rect_item, fill="#ff9800", outline="#e65100")
            self.canvas.itemconfig(text_item, fill="white")
            self.selected_seats.add(seat_id)
            data['selected'] = True

        self.update_total()

    # ---------------------------------------------------------
    # LOGIC CHỌN MÓN (CONCESSION)
    # ---------------------------------------------------------
    def open_concession_dialog(self):
        ConcessionDialog(self, self.controller,
                         initial_selection=self.selected_products,
                         on_confirm=self.on_concession_confirmed)

    def on_concession_confirmed(self, selected_items):
        self.selected_products = selected_items
        self.update_total()

    # ---------------------------------------------------------
    # LOGIC THÀNH VIÊN & GIẢM GIÁ
    # ---------------------------------------------------------
    def on_type_change(self, event):
        selection = self.cbo_type.get()
        if selection == "Người lớn / Thành viên":
            self.e_phone.config(state='normal')
            self.btn_check.config(state='normal', bg="#5c6bc0")
            self.special_discount_percent = 0.0
            if not self.current_customer:
                self.lbl_member_info.config(text="Khách vãng lai (Không giảm)")
        else:
            self.e_phone.delete(0, tk.END)
            self.e_phone.config(state='disabled')
            self.btn_check.config(state='disabled', bg="#ccc")

            self.special_discount_percent = self.controller.get_special_discount(selection)
            self.current_customer = None
            self.member_discount_percent = 0.0
            self.lbl_member_info.config(text="")

        self.update_total()

    def check_member(self):
        if self.cbo_type.get() != "Người lớn / Thành viên": return
        phone = self.e_phone.get().strip()
        if not phone:
            messagebox.showwarning("Thông báo", "Vui lòng nhập SĐT!")
            return

        customer, percent, msg = self.controller.check_member_discount(phone)
        self.current_customer = customer
        self.member_discount_percent = percent

        color = "green" if customer else "red"
        self.lbl_member_info.config(text=msg, fg=color)
        self.update_total()

    # ---------------------------------------------------------
    # TÍNH TIỀN (QUAN TRỌNG)
    # ---------------------------------------------------------
    def update_total(self):
        # 1. Tiền Vé (Float)
        seat_count = len(self.selected_seats)
        ticket_total = seat_count * float(self.st.ticket_price)

        # 2. Tiền Đồ ăn (Float) - FIX LỖI DECIMAL
        food_total = 0.0
        if self.selected_products:
            # Ép kiểu float cho giá sản phẩm (tránh lỗi Decimal + Float)
            food_total = sum(float(item['obj'].price) * item['qty'] for item in self.selected_products.values())

            # Text hiển thị món
            food_text = "\n".join([f"{v['obj'].name} x{v['qty']}" for v in self.selected_products.values()])
            self.lbl_food_list.config(text=food_text, fg="#333")
        else:
            self.lbl_food_list.config(text="Chưa chọn món", fg="#555")

        # 3. Tổng tạm tính
        grand_subtotal = ticket_total + food_total

        # 4. Tính giảm giá
        if self.special_discount_percent > 0:
            final_percent = self.special_discount_percent
            note = f"Ưu đãi {self.cbo_type.get()}"
        else:
            final_percent = self.member_discount_percent
            note = "Ưu đãi Thành viên"

        discount_amount = grand_subtotal * final_percent
        final_total = grand_subtotal - discount_amount
        self.final_total_amount = final_total

        # 5. Cập nhật UI
        seat_labels = []
        for rect, d in self.seat_objects.items():
            if 'parent' not in d and d['selected']: seat_labels.append(d['lbl'])

        self.lbl_seat_list.config(text=f"Ghế: {', '.join(seat_labels)}")
        self.lbl_subtotal.config(text=f"Tạm tính (Vé+Đồ ăn): {int(grand_subtotal):,} đ")

        if discount_amount > 0:
            self.lbl_discount.config(text=f"Giảm giá ({note}): -{int(discount_amount):,} đ")
        else:
            self.lbl_discount.config(text="")

        self.lbl_total.config(text=f"TỔNG: {int(final_total):,} VND")

        # Import class vừa tạo ở trên đầu file
        # from views.payment_dialog import PaymentConfirmDialog (nếu để file riêng)
        # Hoặc nếu để chung file thì không cần import

    def on_payment(self):
        if not self.selected_seats:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ghế!")
            return

        # Hàm xử lý thực sự khi đã xác nhận
        def do_process_payment():
            cus_id = self.current_customer.customer_id if self.current_customer else None

            # Chuẩn bị danh sách sản phẩm
            prod_list_to_save = []
            for pid, item in self.selected_products.items():
                prod_list_to_save.append((pid, item['qty'], item['obj'].price))

            success, msg = self.controller.process_payment(
                self.st.showtime_id,
                self.user_id,
                list(self.selected_seats),
                self.final_total_amount,
                customer_id=cus_id,
                products_list=prod_list_to_save
            )

            if success:
                messagebox.showinfo("Thành công", "Đã xuất vé thành công!")
                self.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

        # --- THAY ĐỔI: Không hỏi Yes/No nữa, mà mở Dialog tính tiền ---
        # Gọi PaymentConfirmDialog
        PaymentConfirmDialog(self, self.final_total_amount, on_confirm=do_process_payment)