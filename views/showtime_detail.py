import tkinter as tk
from tkinter import ttk
from dao.seat_dao import SeatDAO


class ShowtimeDetail(tk.Toplevel):
    def __init__(self, parent, controller, st_id):
        super().__init__(parent)
        self.controller = controller
        self.st_id = st_id
        self.seat_dao = SeatDAO()

        self.title("Chi tiết suất chiếu")
        # 1. TĂNG CHIỀU RỘNG CỬA SỔ LÊN 1250
        self.geometry("1250x700")
        self.config(bg="#f0f2f5")

        self.st = self.controller.get_detail(st_id)
        if not self.st:
            self.destroy()
            return

        self.render_ui()

    def render_ui(self):
        # --- CỘT TRÁI (INFO) ---
        # Giữ nguyên width=350 cho cột thông tin
        left_panel = tk.Frame(self, bg="#f5f6f8", width=350, relief="solid", bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="Chi tiết suất chiếu", font=("Arial", 16, "bold"), bg="#e0e0e0", fg="#333",
                 anchor="w", padx=20, pady=15).pack(fill=tk.X)
        content_left = tk.Frame(left_panel, bg="#f5f6f8", padx=20, pady=20)
        content_left.pack(fill=tk.BOTH, expand=True)

        def add_info(label, val):
            tk.Label(content_left, text=label, font=("Arial", 10, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(10, 0))
            tk.Label(content_left, text=val, font=("Arial", 12), bg="#f5f6f8", fg="#333").pack(anchor="w", pady=(2, 0))

        add_info("Tên phim", self.st.movie.title)
        add_info("Ngày chiếu", self.st.start_time.strftime("%d-%m-%Y"))
        add_info("Phòng chiếu", f"Phòng: {self.st.room.room_name}")

        tk.Label(content_left, text="Giá vé", font=("Arial", 10, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                        pady=(10, 0))
        price_frame = tk.Frame(content_left, bg="#f5f6f8")
        price_frame.pack(anchor="w", pady=(2, 0))
        tk.Label(price_frame, text=f"{int(self.st.ticket_price):,}", font=("Arial", 12), bg="#f5f6f8", fg="#666").pack(
            side=tk.LEFT)
        tk.Label(price_frame, text="Thay đổi", font=("Arial", 10), bg="#f5f6f8", fg="#5c9aff", cursor="hand2").pack(
            side=tk.LEFT, padx=10)

        tk.Label(content_left, text="Các suất chiếu", font=("Arial", 10, "bold"), bg="#f5f6f8", fg="#333").pack(
            anchor="w", pady=(15, 5))
        tk.Label(content_left, text=self.st.start_time.strftime("%H:%M:%S"), font=("Arial", 11, "bold"), bg="white",
                 fg="black", bd=1, relief="solid", padx=15, pady=5).pack(anchor="w")

        btn_frame = tk.Frame(left_panel, bg="#f5f6f8", pady=20, padx=20)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(btn_frame, text="Xoá", bg="#ff5722", fg="white", font=("Arial", 10, "bold"), width=10,
                  relief="flat").pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Thoát", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), width=10,
                  relief="flat", command=self.destroy).pack(side=tk.RIGHT)

        # --- CỘT PHẢI (SEAT MAP) ---
        right_panel = tk.Frame(self, bg="white")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right_panel, text="Danh sách ghế", font=("Arial", 16, "bold"), bg="#e0e0e0", fg="#333", anchor="w",
                 padx=20, pady=15).pack(fill=tk.X)

        # Thống kê
        stats_frame = tk.Frame(right_panel, bg="white", pady=15)
        stats_frame.pack(fill=tk.X)
        all_seats = self.seat_dao.get_seats_by_room(self.st.room_id)
        booked_ids = self.seat_dao.get_booked_seat_ids(self.st.showtime_id)
        total = len(all_seats)
        booked = len(booked_ids)
        empty = total - booked
        tk.Label(stats_frame, text=f"Tổng số ghế: {total}", bg="white", fg="#555").pack(side=tk.LEFT, expand=True)
        tk.Label(stats_frame, text=f"Đã đặt: {booked}", bg="white", fg="#555").pack(side=tk.LEFT, expand=True)
        tk.Label(stats_frame, text=f"Còn trống: {empty}", bg="white", fg="#555").pack(side=tk.LEFT, expand=True)

        # CANVAS VẼ GHẾ
        self.canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        # Bỏ scrollbar ngang vì đã đủ rộng

        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        self.draw_seat_map(all_seats, booked_ids)

    def draw_seat_map(self, all_seats, booked_ids):
        rows_map = {}
        for s in all_seats:
            if s.seat_row not in rows_map: rows_map[s.seat_row] = []
            rows_map[s.seat_row].append(s)

        sorted_rows = sorted(rows_map.keys())
        if not sorted_rows: return

        # 2. ĐIỀU CHỈNH KÍCH THƯỚC GHẾ ĐỂ VỪA VẶN HƠN
        # Giảm kích thước xuống một chút để chứa được 15 cột thoải mái
        SEAT_W, SEAT_H = 36, 30  # Cũ: 40, 30
        GAP_X, GAP_Y = 6, 10  # Cũ: 10, 10
        START_Y = 100

        # Tính toán
        max_cols = 0
        for r in rows_map.values():
            max_cols = max(max_cols, len(r))

        total_width = max_cols * (SEAT_W + GAP_X)

        # Lấy chiều rộng thực tế của Canvas để căn giữa (hoặc giả định nếu chưa render xong)
        canvas_width = 850

        start_x = max(20, (canvas_width - total_width) // 2)

        # 3. Vẽ MÀN HÌNH
        screen_w = total_width + 100
        screen_x_start = start_x - 50
        self.canvas.create_arc(
            screen_x_start, 20, screen_x_start + screen_w, 80,
            start=0, extent=-180, style=tk.ARC, width=3, outline="#999"
        )
        self.canvas.create_text(screen_x_start + screen_w / 2, 60, text="MÀN HÌNH", font=("Arial", 10, "bold"),
                                fill="#999")

        # 4. Vẽ GHẾ
        y = START_Y
        for r_name in sorted_rows:
            seats = sorted(rows_map[r_name], key=lambda x: x.seat_number)

            row_width = len(seats) * (SEAT_W + GAP_X)
            x = start_x + (total_width - row_width) // 2

            for s in seats:
                is_booked = s.seat_id in booked_ids

                fill_color = "white" if not is_booked else "#555"
                text_color = "#2e7d32" if not is_booked else "white"
                outline_color = "#2e7d32" if not is_booked else "#555"

                self.canvas.create_rectangle(
                    x, y, x + SEAT_W, y + SEAT_H,
                    fill=fill_color, outline=outline_color, width=1.5,
                    tags=f"seat_{s.seat_id}"
                )

                seat_label = f"{s.seat_row}{s.seat_number}"
                self.canvas.create_text(
                    x + SEAT_W / 2, y + SEAT_H / 2,
                    text=seat_label, font=("Arial", 8, "bold"), fill=text_color,
                    tags=f"seat_{s.seat_id}"
                )

                x += SEAT_W + GAP_X

            y += SEAT_H + GAP_Y

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))