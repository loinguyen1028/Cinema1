import tkinter as tk
from tkinter import ttk, messagebox
from dao.seat_dao import SeatDAO
from views.concession_dialog import ConcessionDialog
from views.payment_dialog import PaymentConfirmDialog
from views.ticket_success_dialog import TicketSuccessDialog


class BookingDialog(tk.Toplevel):
    def __init__(self, parent, controller, st_id, current_user_id):
        super().__init__(parent)
        self.controller = controller
        self.st_id = st_id
        self.user_id = current_user_id
        self.seat_dao = SeatDAO()

        self.title("🎬 Bán vé & Thanh toán")
        self.geometry("1250x750")
        self.config(bg="#121212")
        self.grab_set()

        # ================= THEME =================
        self.colors = {
            "bg": "#121212",
            "panel": "#1a1a1a",
            "card": "#202020",
            "text": "#ffffff",
            "muted": "#aaaaaa",
            "gold": "#f5c518",
            "gold_dark": "#d4af37",
            "danger": "#e53935",
            "seat_free": "#ffffff",
            "seat_booked": "#555555",
            "seat_select": "#f5c518",
            "seat_outline": "#f5c518"
        }

        self.st = self.controller.get_detail(st_id)

        self.selected_seats = set()
        self.seat_objects = {}

        self.current_customer = None
        self.member_discount_percent = 0.0
        self.special_discount_percent = 0.0
        self.final_total_amount = 0
        self.selected_products = {}

        if not self.st:
            self.destroy()
            return

        self.render_ui()

    # ==================================================
    # UI
    # ==================================================
    def render_ui(self):
        # ---------------- LEFT PANEL ----------------
        left = tk.Frame(self, bg=self.colors["panel"], width=360)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(
            left,
            text=self.st.movie.title.upper(),
            font=("Arial", 17, "bold"),
            fg=self.colors["gold"],
            bg=self.colors["panel"],
            wraplength=320
        ).pack(pady=(25, 10), padx=20)

        info = tk.Frame(left, bg=self.colors["card"], padx=15, pady=15)
        info.pack(fill=tk.X, padx=20)

        def info_row(l, v):
            r = tk.Frame(info, bg=self.colors["card"])
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=l, bg=self.colors["card"], fg=self.colors["muted"],
                     font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(r, text=v, bg=self.colors["card"], fg=self.colors["text"],
                     font=("Arial", 10)).pack(side=tk.RIGHT)

        info_row("Phòng:", self.st.room.room_name)
        info_row("Ngày:", self.st.start_time.strftime("%d/%m/%Y"))
        info_row("Suất:", self.st.start_time.strftime("%H:%M"))
        info_row("Giá vé:", f"{int(self.st.ticket_price):,} đ")

        # -------- ƯU ĐÃI --------
        promo = tk.LabelFrame(
            left, text="ƯU ĐÃI & THÀNH VIÊN",
            bg=self.colors["panel"],
            fg=self.colors["gold"],
            font=("Arial", 10, "bold")
        )
        promo.pack(fill=tk.X, padx=20, pady=10)

        f_type = tk.Frame(promo, bg=self.colors["panel"])
        f_type.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f_type, text="Đối tượng:", bg=self.colors["panel"],
                 fg=self.colors["muted"]).pack(side=tk.LEFT)

        self.cbo_type = ttk.Combobox(
            f_type,
            values=["Người lớn / Thành viên", "Sinh viên", "Trẻ em"],
            state="readonly",
            width=20
        )
        self.cbo_type.current(0)
        self.cbo_type.pack(side=tk.RIGHT)
        self.cbo_type.bind("<<ComboboxSelected>>", self.on_type_change)

        self.f_phone = tk.Frame(promo, bg=self.colors["panel"])
        self.f_phone.pack(fill=tk.X, padx=10, pady=5)

        self.e_phone = tk.Entry(self.f_phone)
        self.e_phone.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            self.f_phone,
            text="Kiểm tra",
            bg=self.colors["gold"],
            fg="black",
            command=self.check_member,
            relief="flat"
        ).pack(side=tk.RIGHT, padx=5)

        self.lbl_member_info = tk.Label(
            promo,
            text="Khách vãng lai (Không giảm)",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Arial", 9, "italic")
        )
        self.lbl_member_info.pack(anchor="w", padx=10, pady=5)

        # -------- BẮP NƯỚC --------
        food = tk.LabelFrame(
            left, text="BẮP & NƯỚC",
            bg=self.colors["panel"],
            fg=self.colors["gold"],
            font=("Arial", 10, "bold")
        )
        food.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            food, text="🍿 Chọn món",
            bg=self.colors["gold_dark"],
            fg="black",
            relief="flat",
            command=self.open_concession_dialog
        ).pack(side=tk.RIGHT, padx=10, pady=10)

        self.lbl_food_list = tk.Label(
            food,
            text="Chưa chọn món",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            wraplength=240,
            justify="left"
        )
        self.lbl_food_list.pack(side=tk.LEFT, padx=10, pady=10)

        # -------- THANH TOÁN --------
        tk.Label(
            left,
            text="THANH TOÁN",
            bg=self.colors["panel"],
            fg=self.colors["gold"],
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 5))

        self.lbl_seat_list = tk.Label(left, text="Ghế: -",
                                      bg=self.colors["panel"],
                                      fg=self.colors["gold"])
        self.lbl_seat_list.pack()

        self.lbl_subtotal = tk.Label(left, bg=self.colors["panel"], fg=self.colors["muted"])
        self.lbl_subtotal.pack()

        self.lbl_discount = tk.Label(left, bg=self.colors["panel"], fg="lightgreen")
        self.lbl_discount.pack()

        self.lbl_total = tk.Label(
            left,
            text="TỔNG: 0 VND",
            bg=self.colors["panel"],
            fg=self.colors["danger"],
            font=("Arial", 18, "bold")
        )
        self.lbl_total.pack(pady=10)

        btns = tk.Frame(left, bg=self.colors["panel"])
        btns.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=25)

        tk.Button(btns, text="Hủy", width=10, command=self.destroy).pack(side=tk.LEFT)
        tk.Button(
            btns, text="THANH TOÁN",
            bg=self.colors["gold"],
            fg="black",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.on_payment
        ).pack(side=tk.RIGHT)

        # ---------------- RIGHT PANEL (SEATS) ----------------
        right = tk.Frame(self, bg=self.colors["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            right,
            text="SƠ ĐỒ GHẾ",
            bg=self.colors["bg"],
            fg=self.colors["gold"],
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        self.canvas = tk.Canvas(right, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_seat_map()

    # ==================================================
    # SEAT MAP
    # ==================================================
    def load_seat_map(self):
        all_seats = self.seat_dao.get_seats_by_room(self.st.room_id)
        booked_ids = self.seat_dao.get_booked_seat_ids(self.st.showtime_id)
        self.draw_interactive_map(all_seats, booked_ids)

    def draw_interactive_map(self, all_seats, booked_ids):
        rows = {}
        for s in all_seats:
            rows.setdefault(s.seat_row, []).append(s)

        SEAT_W, SEAT_H = 36, 30
        GAP_X, GAP_Y = 6, 10

        self.seat_objects = {}

        # ===============================
        # 🎬 VẼ MÀN HÌNH CHIẾU
        # ===============================
        max_cols = max(len(v) for v in rows.values()) if rows else 0
        total_width = max_cols * (SEAT_W + GAP_X)
        start_x = max(80, (900 - total_width) // 2)

        screen_y = 30
        screen_h = 32
        screen_w = total_width + 120
        screen_x = start_x - 60

        # Bóng
        self.canvas.create_rectangle(
            screen_x + 6, screen_y + 6,
            screen_x + screen_w + 6, screen_y + screen_h + 6,
            fill="#111", outline=""
        )

        # Thân màn hình
        self.canvas.create_rectangle(
            screen_x, screen_y,
            screen_x + screen_w, screen_y + screen_h,
            fill="#e0e0e0", outline="#999", width=2
        )

        # Ánh sáng hắt
        self.canvas.create_rectangle(
            screen_x, screen_y + screen_h,
                      screen_x + screen_w, screen_y + screen_h + 18,
            fill="#f5f5f5", outline=""
        )

        self.canvas.create_text(
            screen_x + screen_w / 2,
            screen_y + screen_h / 2,
            text="MÀN HÌNH",
            font=("Arial", 11, "bold"),
            fill="#555"
        )

        # ===============================
        # 🎟️ VẼ GHẾ
        # ===============================
        y = screen_y + screen_h + 40  # Cách màn hình

        for r in sorted(rows):
            x = start_x
            for s in sorted(rows[r], key=lambda x: x.seat_number):
                booked = s.seat_id in booked_ids

                color = self.colors["seat_booked"] if booked else self.colors["seat_free"]
                outline = self.colors["seat_booked"] if booked else self.colors["seat_outline"]

                rect = self.canvas.create_rectangle(
                    x, y, x + SEAT_W, y + SEAT_H,
                    fill=color, outline=outline, width=1.5
                )
                text = self.canvas.create_text(
                    x + SEAT_W / 2, y + SEAT_H / 2,
                    text=f"{s.seat_row}{s.seat_number}",
                    fill="white" if booked else "black",
                    font=("Arial", 8, "bold")
                )

                if not booked:
                    self.seat_objects[rect] = {
                        "id": s.seat_id,
                        "lbl": f"{s.seat_row}{s.seat_number}",
                        "text": text,
                        "selected": False
                    }
                    self.canvas.tag_bind(rect, "<Button-1>",
                                         lambda e, r=rect: self.toggle_seat(r))
                    self.canvas.tag_bind(text, "<Button-1>",
                                         lambda e, r=rect: self.toggle_seat(r))

                x += SEAT_W + GAP_X
            y += SEAT_H + GAP_Y

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_seat(self, rect):
        d = self.seat_objects.get(rect)
        if not d:
            return

        if d["selected"]:
            self.canvas.itemconfig(rect, fill=self.colors["seat_free"])
            self.selected_seats.remove(d["id"])
        else:
            self.canvas.itemconfig(rect, fill=self.colors["seat_select"])
            self.selected_seats.add(d["id"])

        d["selected"] = not d["selected"]
        self.update_total()

    # ==================================================
    # LOGIC KHÁC (GIỮ NGUYÊN)
    # ==================================================
    def open_concession_dialog(self):
        ConcessionDialog(self, self.controller,
                         initial_selection=self.selected_products,
                         on_confirm=self.on_concession_confirmed)

    def on_concession_confirmed(self, selected_items):
        self.selected_products = selected_items
        self.update_total()

    def on_type_change(self, event):
        cust_type = self.cbo_type.get()

        # 2. Nếu là Sinh viên hoặc Trẻ em -> Gọi Controller lấy % giảm giá
        if cust_type in ["Sinh viên", "Trẻ em"]:
            # Hàm này sẽ gọi xuống Service để lấy mức giảm (ví dụ 0.2 hoặc 0.5)
            self.special_discount_percent = self.controller.get_special_discount(cust_type)
        else:
            # Nếu chọn lại "Người lớn" thì reset về 0
            self.special_discount_percent = 0.0

        self.update_total()

    def check_member(self):
        phone = self.e_phone.get().strip()
        customer, percent, msg = self.controller.check_member_discount(phone)
        self.current_customer = customer
        self.member_discount_percent = percent
        self.lbl_member_info.config(text=msg, fg="lightgreen" if customer else "red")
        self.update_total()

    def update_total(self):
        # 1. Tính tiền vé
        ticket_total = len(self.selected_seats) * float(self.st.ticket_price)

        # 2. Tính tiền bắp nước
        food_total = 0
        food_text_list = []

        if self.selected_products:
            for v in self.selected_products.values():
                food_total += float(v["obj"].price) * v["qty"]
                p_name = getattr(v["obj"], "name", "Món")
                # Thêm dấu gạch đầu dòng cho đẹp
                food_text_list.append(f"- {v['qty']}x {p_name}")

            # ===> SỬA: Dùng xuống dòng (\n) thay vì dấu phẩy
            food_display_str = "\n".join(food_text_list)
        else:
            food_display_str = "Chưa chọn món"

        subtotal = ticket_total + food_total

        # ===> ĐOẠN SỬA ĐỔI QUAN TRỌNG <===
        # So sánh giữa Giảm giá thành viên (SĐT) và Giảm giá đối tượng (SV/Trẻ em)
        # Cái nào cao hơn thì lấy cái đó (Tránh cộng dồn lỗ vốn)
        # Ví dụ: Thành viên giảm 5%, nhưng Sinh viên giảm 20% -> Lấy 20%
        final_discount_percent = max(self.member_discount_percent, self.special_discount_percent)

        discount = subtotal * final_discount_percent
        final = subtotal - discount
        self.final_total_amount = final
        # =================================

        # Cập nhật giao diện
        seats = [d["lbl"] for d in self.seat_objects.values() if d["selected"]]
        self.lbl_seat_list.config(text=f"Ghế: {', '.join(seats)}")

        self.lbl_food_list.config(text=food_display_str, wraplength=300, justify="left")

        self.lbl_subtotal.config(text=f"Tạm tính: {int(subtotal):,} đ")

        # Hiển thị rõ giảm bao nhiêu tiền và bao nhiêu %
        if discount > 0:
            percent_text = int(final_discount_percent * 100)
            self.lbl_discount.config(
                text=f"Giảm giá: -{int(discount):,} đ ({percent_text}%)",
                fg="lightgreen"
            )
        else:
            self.lbl_discount.config(text="")

        self.lbl_total.config(text=f"TỔNG: {int(final):,} VND")

    def on_payment(self):
        if not self.selected_seats:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ghế!")
            return

        def do_pay():

            cus_id = self.current_customer.customer_id if self.current_customer else None

            success, msg = self.controller.process_payment(
                self.st.showtime_id,
                self.user_id,
                list(self.selected_seats),
                self.final_total_amount,
                customer_id = cus_id
            )

            if success:
                # 1. Lấy tên người bán
                seller_name = self.controller.get_user_name(self.user_id)

                # 2. Tạo chuỗi ghế
                seat_labels = ", ".join(
                    d["lbl"] for d in self.seat_objects.values() if d["selected"]
                )

                # 3. Lấy Ticket ID từ thông báo
                import re
                ticket_id = "UNKNOWN"
                match = re.search(r"Mã vé:\s*(\d+)", msg)
                if match:
                    ticket_id = match.group(1)

                # 4. Tạo chuỗi danh sách Bắp/Nước
                food_str_for_print = ""
                if self.selected_products:
                    items = []
                    for v in self.selected_products.values():
                        p_name = getattr(v["obj"], "name", "Món")
                        items.append(f"{v['qty']}x {p_name}")
                    food_str_for_print = ", ".join(items)
                # ============================

                # 5. Đóng gói dữ liệu in vé
                ticket_data = {
                    "movie_name": self.st.movie.title,
                    "format": "2D/Digital",
                    "room": self.st.room.room_name,
                    "seat": seat_labels,
                    "date": self.st.start_time.strftime("%d/%m/%Y"),
                    "time": self.st.start_time.strftime("%H:%M"),
                    "price": int(self.final_total_amount),
                    "ticket_id": ticket_id,
                    "seller": seller_name,
                    "food": food_str_for_print
                }

                TicketSuccessDialog(
                    self,
                    total_amount=self.final_total_amount,
                    seat_labels=seat_labels,
                    on_close=self.destroy,
                    ticket_data=ticket_data
                )
            else:
                messagebox.showerror("Lỗi", msg)

        PaymentConfirmDialog(self, self.final_total_amount, on_confirm=do_pay)
