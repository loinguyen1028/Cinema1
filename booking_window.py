# booking_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from psycopg2.extras import Json


class BookingWindow(tk.Toplevel):
    """
    Màn hình Bán vé:
    - Chọn / lưu khách hàng
    - Chọn phim + suất chiếu
    - Hiển thị sơ đồ ghế giống ảnh (ghế chọn: vàng, đã mua: xám)
    - Tính Tổng tiền và lưu vé vào DB
    """
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.title("Bán Vé / Đặt Vé")
        self.geometry("1000x700")
        self.user_id = user_id

        self.selected_showtime_id = None
        self.current_customer_id = None
        self.current_price = 0.0   # giá 1 ghế của suất chiếu
        self.seat_buttons = {}     # seat_id -> {"button": btn, "selected": bool}

        # ========== KHUNG KHÁCH HÀNG ==========
        customer_frame = tk.LabelFrame(self, text="Thông tin khách hàng")
        customer_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(customer_frame, text="SĐT:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.entry_phone = tk.Entry(customer_frame, width=20)
        self.entry_phone.grid(row=0, column=1, padx=5, pady=2)

        tk.Button(customer_frame, text="Tìm",
                  command=self.find_customer).grid(row=0, column=2, padx=5, pady=2)

        tk.Label(customer_frame, text="Tên khách:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.entry_name = tk.Entry(customer_frame, width=30)
        self.entry_name.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(customer_frame, text="Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.entry_email = tk.Entry(customer_frame, width=30)
        self.entry_email.grid(row=2, column=1, padx=5, pady=2)

        tk.Button(customer_frame, text="Lưu / Cập nhật khách",
                  command=self.save_customer).grid(row=1, column=2, rowspan=2, padx=5, pady=2)

        # ========== KHUNG CHỌN PHIM + SUẤT CHIẾU ==========
        show_frame = tk.LabelFrame(self, text="Chọn phim & suất chiếu")
        show_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(show_frame, text="Phim:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.cbo_movie = ttk.Combobox(show_frame, state="readonly", width=40)
        self.cbo_movie.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.cbo_movie.bind("<<ComboboxSelected>>", self.on_movie_selected)

        tk.Label(show_frame, text="Suất chiếu:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.cbo_showtime = ttk.Combobox(show_frame, state="readonly", width=60)
        self.cbo_showtime.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.cbo_showtime.bind("<<ComboboxSelected>>", self.on_showtime_selected)

        self.lbl_price = tk.Label(show_frame, text="Giá vé: 0 VND")
        self.lbl_price.grid(row=1, column=2, padx=5, pady=2)

        self.load_movies()

        # ========== KHUNG SƠ ĐỒ GHẾ (giống ảnh) ==========
        self.seat_frame = tk.LabelFrame(self, text="Sơ đồ ghế")
        self.seat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Thanh màu xanh “Màn Chiếu”
        screen_lbl = tk.Label(
            self.seat_frame, text="Màn Chiếu",
            bg="blue", fg="white",
            font=("Arial", 14, "bold")
        )
        screen_lbl.pack(fill=tk.X, padx=40, pady=10)

        # Khung chứa sơ đồ ghế + chú thích
        body = tk.Frame(self.seat_frame, bg="black")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Grid ghế (trái)
        self.seat_grid_frame = tk.Frame(body, bg="black")
        self.seat_grid_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Chú thích (phải)
        legend = tk.Frame(body, bg="white")
        legend.pack(side=tk.LEFT, padx=40, pady=10, fill=tk.Y)

        tk.Label(legend, text="<= Lối vào", bg="white", fg="black",
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=5)

        row1 = tk.Frame(legend, bg="white")
        row1.pack(anchor="w", pady=5)
        tk.Label(row1, width=2, bg="yellow").pack(side=tk.LEFT, padx=5)
        tk.Label(row1, text="Đang chọn", bg="white").pack(side=tk.LEFT)

        row2 = tk.Frame(legend, bg="white")
        row2.pack(anchor="w", pady=5)
        tk.Label(row2, width=2, bg="grey").pack(side=tk.LEFT, padx=5)
        tk.Label(row2, text="Đã mua", bg="white").pack(side=tk.LEFT)

        # ========== KHUNG DƯỚI: Tổng tiền & Thanh toán ==========
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        self.lbl_total = tk.Label(bottom_frame, text="Tổng tiền: 0 VND",
                                  font=("Arial", 12, "bold"), fg="red")
        self.lbl_total.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom_frame, text="Thanh toán (Lưu vé)",
                  bg="yellow", command=self.save_ticket).pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom_frame, text="Hủy", bg="red", fg="white",
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
    def ask_payment_info(self, total_amount):
        dialog = tk.Toplevel(self)
        dialog.title("Phương thức thanh toán")
        dialog.grab_set()

        tk.Label(dialog, text=f"Tổng tiền: {total_amount:.0f} VND",
                 font=("Arial", 12, "bold")).pack(padx=10, pady=10)

        method_var = tk.StringVar(value="Tiền mặt")
        methods = ["Tiền mặt", "Thẻ", "Momo", "ZaloPay", "Chuyển khoản"]

        tk.Label(dialog, text="Chọn phương thức thanh toán:")\
            .pack(anchor="w", padx=10)

        for m in methods:
            tk.Radiobutton(dialog, text=m, value=m, variable=method_var)\
                .pack(anchor="w", padx=20)

        # Mã giảm giá
        tk.Label(dialog, text="Mã giảm giá (nếu có):").pack(anchor="w", padx=10, pady=(10, 0))
        entry_code = tk.Entry(dialog)
        entry_code.pack(fill="x", padx=10)

        # Số tiền giảm
        tk.Label(dialog, text="Số tiền giảm (VND):").pack(anchor="w", padx=10, pady=(10, 0))
        entry_discount = tk.Entry(dialog)
        entry_discount.insert(0, "0")
        entry_discount.pack(fill="x", padx=10)

        result = {"data": None}

        def on_ok():
            code = entry_code.get().strip() or None
            try:
                discount = float(entry_discount.get() or "0")
            except ValueError:
                messagebox.showwarning("Sai dữ liệu", "Số tiền giảm phải là số",
                                       parent=dialog)
                return

            paid = max(total_amount - discount, 0)

            result["data"] = {
                "method": method_var.get(),
                "discount_code": code,
                "discount_amount": discount,
                "total_amount": total_amount,
                "paid_amount": paid
            }
            dialog.destroy()

        def on_cancel():
            result["data"] = None
            dialog.destroy()

        tk.Button(dialog, text="Xác nhận", command=on_ok).pack(pady=10)
        tk.Button(dialog, text="Hủy", command=on_cancel).pack()

        dialog.wait_window()
        return result["data"]

    # ================== PHẦN KHÁCH HÀNG ==================
    def find_customer(self):
        phone = self.entry_phone.get().strip()
        if not phone:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập số điện thoại")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT customer_id, name, email
                FROM customers
                WHERE phone = %s
            """, (phone,))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        if row:
            self.current_customer_id, name, email = row
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, name)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, email)
        else:
            self.current_customer_id = None
            messagebox.showinfo("Không tìm thấy",
                                "Chưa có khách này, hãy nhập tên & email rồi bấm Lưu.")

    def save_customer(self):
        phone = self.entry_phone.get().strip()
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()

        if not phone or not name:
            messagebox.showwarning("Thiếu dữ liệu",
                                   "Cần nhập ít nhất SĐT và Tên")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            if self.current_customer_id:
                cur.execute("""
                    UPDATE customers
                    SET name=%s, phone=%s, email=%s
                    WHERE customer_id=%s
                """, (name, phone, email, self.current_customer_id))
            else:
                cur.execute("""
                    INSERT INTO customers (name, phone, email)
                    VALUES (%s, %s, %s)
                    RETURNING customer_id
                """, (name, phone, email))
                self.current_customer_id = cur.fetchone()[0]
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã lưu thông tin khách hàng")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # ================== PHẦN PHIM & SUẤT CHIẾU ==================
    def load_movies(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT movie_id, title FROM movies ORDER BY title")
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        self.movie_map = {f"{title} (ID {mid})": mid for mid, title in rows}
        self.cbo_movie["values"] = list(self.movie_map.keys())

    def on_movie_selected(self, event=None):
        key = self.cbo_movie.get()
        if not key:
            return
        movie_id = self.movie_map[key]
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT s.showtime_id,
                       s.start_time,
                       s.ticket_price,
                       r.room_name
                FROM showtimes s
                JOIN rooms r ON s.room_id = r.room_id
                WHERE s.movie_id = %s
                ORDER BY s.start_time
            """, (movie_id,))
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        self.showtime_map = {}
        values = []
        for sid, start_time, price, room_name in rows:
            txt = f"{start_time} - {room_name} - {price} VND"
            values.append(txt)
            self.showtime_map[txt] = (sid, float(price), room_name)

        self.cbo_showtime["values"] = values
        self.cbo_showtime.set("")
        self.selected_showtime_id = None
        self.clear_seats()

    def on_showtime_selected(self, event=None):
        text = self.cbo_showtime.get()
        if not text:
            return
        sid, price, room_name = self.showtime_map[text]
        self.selected_showtime_id = sid
        self.current_price = price
        self.lbl_price.config(text=f"Giá vé: {price:.0f} VND")
        self.load_seats_for_showtime(sid)

    # ================== PHẦN GHẾ NGỒI ==================
    def clear_seats(self):
        for w in self.seat_grid_frame.winfo_children():
            w.destroy()
        self.seat_buttons.clear()
        self.update_total()

    def load_seats_for_showtime(self, showtime_id):
        self.clear_seats()

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Lấy room_id và giá vé (nếu muốn kiểm tra lại)
            cur.execute("""
                SELECT room_id, ticket_price
                FROM showtimes
                WHERE showtime_id = %s
            """, (showtime_id,))
            room_id, price = cur.fetchone()
            self.current_price = float(price)

            # Tất cả ghế của phòng
            cur.execute("""
                SELECT seat_id, seat_row, seat_number
                FROM seats
                WHERE room_id = %s
                ORDER BY seat_row, seat_number
            """, (room_id,))
            seats = cur.fetchall()

            # Ghế đã bán cho suất chiếu này
            cur.execute("""
                SELECT ts.seat_id
                FROM ticket_seats ts
                JOIN tickets t ON ts.ticket_id = t.ticket_id
                WHERE t.showtime_id = %s
            """, (showtime_id,))
            sold_ids = {row[0] for row in cur.fetchall()}

            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        # Tạo grid ghế: A-1, A-2,... với màu
        current_row = None
        row_index = -1

        for seat_id, srow, snum in seats:
            if srow != current_row:
                current_row = srow
                row_index += 1

            col_index = snum - 1  # cột từ 0

            code = f"{srow}-{snum}"

            if seat_id in sold_ids:
                # ghế đã mua: xám, không bấm được
                btn = tk.Button(
                    self.seat_grid_frame,
                    text=code,
                    width=4,
                    bg="grey",
                    fg="white",
                    state=tk.DISABLED
                )
            else:
                btn = tk.Button(
                    self.seat_grid_frame,
                    text=code,
                    width=4,
                    bg="#eeeeee",
                    command=lambda sid=seat_id: self.toggle_seat(sid)
                )
                self.seat_buttons[seat_id] = {"button": btn, "selected": False}

            btn.grid(row=row_index, column=col_index, padx=2, pady=2)

        self.update_total()

    def toggle_seat(self, seat_id):
        info = self.seat_buttons.get(seat_id)
        if not info:
            return
        # Đổi trạng thái
        info["selected"] = not info["selected"]
        btn = info["button"]
        if info["selected"]:
            btn.config(bg="yellow")
        else:
            btn.config(bg="#eeeeee")
        self.update_total()

    def update_total(self):
        count = sum(1 for info in self.seat_buttons.values() if info["selected"])
        total = count * self.current_price
        self.lbl_total.config(text=f"Tổng tiền: {total:.0f} VND")

    # ================== LƯU VÉ ==================
    def save_ticket(self):
        if not self.selected_showtime_id:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn suất chiếu")
            return
        if not self.current_customer_id:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có khách hàng")
            return

        selected_seat_ids = [
            sid for sid, info in self.seat_buttons.items()
            if info["selected"]
        ]
        if not selected_seat_ids:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn ghế")
            return

        total = len(selected_seat_ids) * self.current_price

        # 👉 Hỏi popup chọn phương thức thanh toán
        payment_info = self.ask_payment_info(total)
        if payment_info is None:
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO tickets (showtime_id, customer_id, user_id, total_amount, payment_info)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING ticket_id
            """, (
                self.selected_showtime_id,
                self.current_customer_id,
                self.user_id,
                total,
                Json(payment_info)
            ))
            ticket_id = cur.fetchone()[0]

            for sid in selected_seat_ids:
                cur.execute("""
                    INSERT INTO ticket_seats (ticket_id, seat_id, price)
                    VALUES (%s, %s, %s)
                """, (ticket_id, sid, self.current_price))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Thành công",
                f"Đã thanh toán vé #{ticket_id}\n"
                f"Phương thức: {payment_info['method']}\n"
                f"Tổng tiền: {total:.0f} VND\n"
                f"Giảm giá: {payment_info['discount_amount']:.0f} VND\n"
                f"Khách trả: {payment_info['paid_amount']:.0f} VND"
            )

            self.destroy()

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
