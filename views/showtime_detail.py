import tkinter as tk
from tkinter import ttk
from dao.seat_dao import SeatDAO


class ShowtimeDetail(tk.Toplevel):
    def __init__(self, parent, controller, st_id):
        super().__init__(parent)
        self.controller = controller
        self.st_id = st_id
        self.seat_dao = SeatDAO()

        # ===== STAFF COLORS =====
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "seat_free": "#22c55e",
            "seat_booked": "#374151"
        }

        self.title("Chi tiết suất chiếu")
        self.geometry("1250x700")
        self.config(bg=self.colors["bg"])
        self.grab_set()

        self.st = self.controller.get_detail(st_id)
        if not self.st:
            self.destroy()
            return

        self.render_ui()

    # =====================================================
    def render_ui(self):
        # ================= LEFT PANEL =================
        left_panel = tk.Frame(
            self,
            bg=self.colors["card"],
            width=360
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Header
        tk.Label(
            left_panel,
            text="CHI TIẾT SUẤT CHIẾU",
            font=("Arial", 15, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["primary"],
            anchor="w",
            padx=20,
            pady=15
        ).pack(fill=tk.X)

        content_left = tk.Frame(
            left_panel,
            bg=self.colors["card"],
            padx=20,
            pady=20
        )
        content_left.pack(fill=tk.BOTH, expand=True)

        def add_info(label, value):
            tk.Label(
                content_left,
                text=label,
                font=("Arial", 10),
                bg=self.colors["card"],
                fg=self.colors["muted"]
            ).pack(anchor="w", pady=(10, 0))
            tk.Label(
                content_left,
                text=value,
                font=("Arial", 13, "bold"),
                bg=self.colors["card"],
                fg=self.colors["text"]
            ).pack(anchor="w")

        add_info("Tên phim", self.st.movie.title)
        add_info("Ngày chiếu", self.st.start_time.strftime("%d/%m/%Y"))
        add_info("Phòng chiếu", f"Phòng {self.st.room.room_name}")

        # Giá vé
        tk.Label(
            content_left,
            text="Giá vé",
            font=("Arial", 10),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="w", pady=(15, 0))

        tk.Label(
            content_left,
            text=f"{int(self.st.ticket_price):,} đ",
            font=("Arial", 14, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(anchor="w")

        # Giờ chiếu
        tk.Label(
            content_left,
            text="Giờ chiếu",
            font=("Arial", 10),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="w", pady=(15, 5))

        tk.Label(
            content_left,
            text=self.st.start_time.strftime("%H:%M"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Arial", 13, "bold"),
            padx=18,
            pady=6
        ).pack(anchor="w")

        # Buttons
        btn_frame = tk.Frame(left_panel, bg=self.colors["card"], padx=20, pady=20)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            btn_frame,
            text="🗑 XÓA",
            bg="#ef4444",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Button(
            btn_frame,
            text="ĐÓNG",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Arial", 10, "bold"),
            width=10,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        ).pack(side=tk.RIGHT)

        # ================= RIGHT PANEL =================
        right_panel = tk.Frame(self, bg=self.colors["bg"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        tk.Label(
            right_panel,
            text="SƠ ĐỒ GHẾ",
            font=("Arial", 16, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["primary"],
            anchor="w",
            padx=20,
            pady=15
        ).pack(fill=tk.X)

        # Stats
        stats_frame = tk.Frame(right_panel, bg=self.colors["bg"], pady=10)
        stats_frame.pack(fill=tk.X)

        all_seats = self.seat_dao.get_seats_by_room(self.st.room_id)
        booked_ids = self.seat_dao.get_booked_seat_ids(self.st.showtime_id)

        total = len(all_seats)
        booked = len(booked_ids)
        empty = total - booked

        def stat(text):
            tk.Label(
                stats_frame,
                text=text,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                font=("Arial", 11)
            ).pack(side=tk.LEFT, expand=True)

        stat(f"Tổng ghế: {total}")
        stat(f"Đã đặt: {booked}")
        stat(f"Còn trống: {empty}")

        # Canvas
        canvas_frame = tk.Frame(right_panel, bg=self.colors["bg"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors["bg"],
            highlightthickness=0
        )
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.draw_seat_map(all_seats, booked_ids)

    # =====================================================
    def draw_seat_map(self, all_seats, booked_ids):
        rows_map = {}
        for s in all_seats:
            rows_map.setdefault(s.seat_row, []).append(s)

        sorted_rows = sorted(rows_map.keys())
        if not sorted_rows:
            return

        SEAT_W, SEAT_H = 36, 30
        GAP_X, GAP_Y = 6, 10
        START_Y = 100

        max_cols = max(len(v) for v in rows_map.values())
        total_width = max_cols * (SEAT_W + GAP_X)
        canvas_width = 850
        start_x = max(20, (canvas_width - total_width) // 2)

        # SCREEN
        screen_w = total_width + 100
        screen_x = start_x - 50
        self.canvas.create_arc(
            screen_x, 20, screen_x + screen_w, 80,
            start=0, extent=-180,
            style=tk.ARC,
            width=3,
            outline=self.colors["muted"]
        )
        self.canvas.create_text(
            screen_x + screen_w / 2,
            60,
            text="MÀN HÌNH",
            font=("Arial", 10, "bold"),
            fill=self.colors["muted"]
        )

        # SEATS
        y = START_Y
        for r_name in sorted_rows:
            seats = sorted(rows_map[r_name], key=lambda x: x.seat_number)
            row_width = len(seats) * (SEAT_W + GAP_X)
            x = start_x + (total_width - row_width) // 2

            for s in seats:
                is_booked = s.seat_id in booked_ids
                fill = self.colors["seat_booked"] if is_booked else self.colors["panel"]
                outline = "#ef4444" if is_booked else self.colors["seat_free"]
                text_color = "#ffffff" if is_booked else self.colors["seat_free"]

                self.canvas.create_rectangle(
                    x, y, x + SEAT_W, y + SEAT_H,
                    fill=fill,
                    outline=outline,
                    width=1.6
                )
                self.canvas.create_text(
                    x + SEAT_W / 2,
                    y + SEAT_H / 2,
                    text=f"{s.seat_row}{s.seat_number}",
                    font=("Arial", 8, "bold"),
                    fill=text_color
                )

                x += SEAT_W + GAP_X
            y += SEAT_H + GAP_Y

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
