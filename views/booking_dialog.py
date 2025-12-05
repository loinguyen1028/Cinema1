import tkinter as tk
from tkinter import ttk, messagebox
from dao.seat_dao import SeatDAO


class BookingDialog(tk.Toplevel):
    def __init__(self, parent, controller, st_id, current_user_id):
        super().__init__(parent)
        self.controller = controller
        self.st_id = st_id
        self.user_id = current_user_id
        self.seat_dao = SeatDAO()

        self.title("Bán vé & Thanh toán")
        self.geometry("1250x750")
        self.config(bg="#f0f2f5")
        self.grab_set()

        self.st = self.controller.get_detail(st_id)

        self.selected_seats = set()
        self.seat_objects = {}

        # Biến tính toán
        self.current_customer = None
        self.member_discount_percent = 0.0  # % giảm của thành viên
        self.special_discount_percent = 0.0  # % giảm của Sinh viên/Trẻ em
        self.final_total_amount = 0

        if not self.st:
            self.destroy()
            return

        self.render_ui()

    def render_ui(self):
        # --- CỘT TRÁI ---
        left_panel = tk.Frame(self, bg="white", width=350, relief="solid", bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Header
        tk.Label(left_panel, text=self.st.movie.title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#0f1746", wraplength=300).pack(pady=(30, 10), padx=20)

        # Info Box
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

        tk.Label(left_panel, text="--------------------", bg="white", fg="#ddd").pack(pady=10)

        # --- [MỚI] KHU VỰC ƯU ĐÃI ---
        promo_frame = tk.LabelFrame(left_panel, text="Ưu đãi & Thành viên", bg="white", font=("Arial", 10, "bold"),
                                    fg="#333")
        promo_frame.pack(fill=tk.X, padx=20, pady=5)

        # 1. Chọn đối tượng (Sinh viên/Trẻ em)
        f_type = tk.Frame(promo_frame, bg="white")
        f_type.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(f_type, text="Đối tượng:", bg="white", fg="#555").pack(side=tk.LEFT)

        self.cbo_type = ttk.Combobox(f_type, values=["Người lớn / Thành viên", "Sinh viên", "Trẻ em"],
                                     font=("Arial", 10), state="readonly", width=18)
        self.cbo_type.current(0)
        self.cbo_type.pack(side=tk.RIGHT)
        self.cbo_type.bind("<<ComboboxSelected>>", self.on_type_change)  # Sự kiện khi chọn

        # 2. Nhập SĐT Thành viên
        self.f_phone = tk.Frame(promo_frame, bg="white")
        self.f_phone.pack(fill=tk.X, padx=10, pady=5)

        self.e_phone = tk.Entry(self.f_phone, font=("Arial", 11), width=15, relief="solid", bd=1)
        self.e_phone.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.e_phone.insert(0, "")
        self.e_phone.bind("<Return>", lambda e: self.check_member())

        # --- SỬA DÒNG NÀY: Gán vào self.btn_check ---
        self.btn_check = tk.Button(self.f_phone, text="Kiểm tra", bg="#5c6bc0", fg="white", font=("Arial", 9),
                                   relief="flat", command=self.check_member)
        self.btn_check.pack(side=tk.RIGHT, padx=5)

        self.lbl_member_info = tk.Label(promo_frame, text="", bg="white", fg="#2e7d32", font=("Arial", 9, "italic"),
                                        wraplength=300)
        self.lbl_member_info.pack(anchor="w", padx=10, pady=(0, 10))

        # --- TÍNH TIỀN ---
        tk.Label(left_panel, text="THANH TOÁN", font=("Arial", 11, "bold"), bg="white", fg="#333").pack(pady=(20, 5))

        self.lbl_seat_list = tk.Label(left_panel, text="Ghế: -", font=("Arial", 10), bg="white", fg="#ff9800",
                                      wraplength=300)
        self.lbl_seat_list.pack(pady=5)

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

        # --- CỘT PHẢI (SƠ ĐỒ GHẾ) ---
        right_panel = tk.Frame(self, bg="#f0f2f5")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Legend
        legend = tk.Frame(right_panel, bg="#f0f2f5", pady=15)
        legend.pack(fill=tk.X, padx=20)
        tk.Label(legend, text="Sơ đồ ghế", font=("Arial", 16, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)
        # (Phần chú thích màu sắc ghế bạn tự thêm vào nếu cần, code cũ đã có)

        # Canvas
        self.canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        self.load_seat_map()

    def load_seat_map(self):
        all_seats = self.seat_dao.get_seats_by_room(self.st.room_id)
        booked_ids = self.seat_dao.get_booked_seat_ids(self.st.showtime_id)
        self.draw_interactive_map(all_seats, booked_ids)

    # --- LOGIC XỬ LÝ MỚI ---

    def on_type_change(self, event):
        """Xử lý khi thay đổi Combobox Đối tượng"""
        selection = self.cbo_type.get()

        if selection == "Người lớn / Thành viên":
            # --- MỞ KHÓA ---
            self.e_phone.config(state='normal')   # Cho phép nhập
            self.btn_check.config(state='normal') # Cho phép bấm nút
            self.btn_check.config(bg="#5c6bc0")   # Trả lại màu xanh

            self.special_discount_percent = 0.0

            # Nếu trước đó đã check thành viên thì giữ nguyên thông tin, nếu chưa thì thôi
            if not self.current_customer:
                self.lbl_member_info.config(text="Khách vãng lai (Không giảm)")

        else:
            # --- KHÓA LẠI ---
            self.e_phone.delete(0, tk.END)          # Xóa chữ đang có
            self.e_phone.config(state='disabled')   # Khóa ô nhập
            self.btn_check.config(state='disabled') # Khóa nút
            self.btn_check.config(bg="#ccc")        # Đổi màu xám cho biết là bị khóa

            # Lấy mức giảm giá từ Controller (Sinh viên/Trẻ em)
            self.special_discount_percent = self.controller.get_special_discount(selection)

            # Reset thông tin thành viên (vì Sinh viên/Trẻ em tính theo vé lẻ, không tính theo membership)
            self.current_customer = None
            self.member_discount_percent = 0.0
            self.lbl_member_info.config(text="")

        self.update_total()

    def check_member(self):
        # Chỉ check khi đang ở chế độ Thành viên
        if self.cbo_type.get() != "Người lớn / Thành viên":
            messagebox.showinfo("Lưu ý", "Vui lòng chọn đối tượng là 'Thành viên' để tích điểm/giảm giá.")
            return

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

    def update_total(self):
        count = len(self.selected_seats)
        subtotal = count * float(self.st.ticket_price)

        # Ưu tiên giảm giá đặc biệt (Sinh viên/Trẻ em) hơn giảm giá thành viên
        # Hoặc cộng dồn tùy chính sách. Ở đây ta lấy cái nào lớn hơn hoặc ưu tiên Special.
        # Logic hiện tại: Nếu có Special (Sinh viên/Trẻ em) thì lấy Special. Nếu không thì lấy Member.

        if self.special_discount_percent > 0:
            final_percent = self.special_discount_percent
            note = f"Ưu đãi {self.cbo_type.get()}"
        else:
            final_percent = self.member_discount_percent
            note = "Ưu đãi Thành viên"

        discount_amount = subtotal * final_percent
        final_total = subtotal - discount_amount
        self.final_total_amount = final_total  # Lưu để thanh toán

        # Update UI text
        seat_labels = []
        for rect, d in self.seat_objects.items():
            if 'parent' not in d and d['selected']:
                seat_labels.append(d['lbl'])

        self.lbl_seat_list.config(text=f"Ghế: {', '.join(seat_labels)}")

        if count > 0:
            self.lbl_subtotal.config(text=f"Tạm tính: {int(subtotal):,} đ")
            if discount_amount > 0:
                self.lbl_discount.config(text=f"Giảm giá ({note}): -{int(discount_amount):,} đ", fg="green")
            else:
                self.lbl_discount.config(text="")
        else:
            self.lbl_subtotal.config(text="")
            self.lbl_discount.config(text="")

        self.lbl_total.config(text=f"TỔNG: {int(final_total):,} VND")

    def on_payment(self):
        if not self.selected_seats:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ghế!")
            return

        cus_id = self.current_customer.customer_id if self.current_customer else None

        if messagebox.askyesno("Xác nhận",
                               f"Thanh toán {len(self.selected_seats)} vé?\nTổng tiền: {int(self.final_total_amount):,} VND"):
            success, msg = self.controller.process_payment(
                self.st.showtime_id,
                self.user_id,
                list(self.selected_seats),
                self.final_total_amount,
                customer_id=cus_id
            )
            if success:
                messagebox.showinfo("Thành công", msg)
                self.destroy()
            else:
                messagebox.showerror("Lỗi", msg)

    # ... (Copy lại hàm draw_interactive_map và toggle_seat từ code cũ) ...
    # Bạn nhớ copy y nguyên 2 hàm vẽ ghế đó vào đây nhé để code chạy được.
    def draw_interactive_map(self, all_seats, booked_ids):
        # (Paste code vẽ ghế cũ vào đây)
        # Code vẽ màn hình cong, vẽ ghế, bind click...
        # Lưu ý: Khi bind click, gọi self.toggle_seat
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