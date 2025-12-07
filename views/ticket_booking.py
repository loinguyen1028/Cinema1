import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
from views.date_picker_popup import DatePickerPopup
from controllers.ticket_controller import TicketController
from views.booking_dialog import BookingDialog


class TicketBooking:
    # --- SỬA LỖI Ở ĐÂY: Thêm tham số user_id=None ---
    def __init__(self, parent_frame, user_id=None):
        self.parent = parent_frame
        self.user_id = user_id  # Lưu user_id để truyền cho BookingDialog
        self.controller = TicketController()

        self.current_date = datetime.now().strftime("%d/%m/%Y")

        self.render()

    def render(self):
        # Container chính
        self.content = tk.Frame(self.parent, bg="white")
        self.content.pack(fill=tk.BOTH, expand=True)

        # 1. Toolbar (Tìm kiếm, Lọc, Ngày)
        self.render_toolbar()

        # 2. Khu vực danh sách phim (Scrollable)
        self.render_scroll_area()

        # 3. Load dữ liệu lần đầu
        self.load_data()

    def render_toolbar(self):
        toolbar = tk.Frame(self.content, bg="white")
        toolbar.pack(fill=tk.X, padx=30, pady=20)

        # --- 1. TÌM KIẾM (Giao diện khung viền) ---
        # Container cho cụm tìm kiếm
        f_search_group = tk.Frame(toolbar, bg="white")
        f_search_group.pack(side=tk.LEFT, padx=(0, 20))

        # Tiêu đề nhỏ bên trên (nếu muốn, hoặc bỏ đi)
        tk.Label(f_search_group, text="Tìm kiếm phim", bg="white", fg="#757575", font=("Arial", 9)).pack(anchor="w",
                                                                                                         pady=(0,
                                                                                                               2))
        search_border = tk.Frame(f_search_group, bg="white", highlightbackground="#bdbdbd", highlightthickness=1)
        search_border.pack(fill=tk.X)

        # Icon kính lúp bên trong khung
        tk.Label(search_border, text="🔍", font=("Arial", 11), bg="white", fg="#757575").pack(side=tk.LEFT,
                                                                                             padx=(8, 2))

        # Ô nhập liệu (bỏ viền mặc định bd=0 để hòa nhập vào khung)
        self.entry_search = tk.Entry(search_border, font=("Arial", 11), width=25, bd=0, bg="white")
        self.entry_search.pack(side=tk.LEFT, ipady=6, padx=(0, 8))
        self.entry_search.bind("<KeyRelease>", self.on_filter_change)

        # Hiệu ứng: Đổi màu viền khi bấm vào
        self.entry_search.bind("<FocusIn>",
                               lambda e: search_border.config(highlightbackground="#1976d2", highlightthickness=2))
        self.entry_search.bind("<FocusOut>",
                               lambda e: search_border.config(highlightbackground="#bdbdbd", highlightthickness=1))

        # --- 2. THỂ LOẠI (Combobox) ---
        f_genre_group = tk.Frame(toolbar, bg="white")
        f_genre_group.pack(side=tk.LEFT)

        tk.Label(f_genre_group, text="Thể loại", bg="white", fg="#757575", font=("Arial", 9)).pack(anchor="w",
                                                                                                   pady=(0, 2))

        self.cbo_genre = ttk.Combobox(f_genre_group,
                                      values=["Tất cả", "Hành động", "Kinh dị", "Hoạt hình", "Tình cảm", "Hài"],
                                      font=("Arial", 11), width=15, state="readonly")
        self.cbo_genre.current(0)
        self.cbo_genre.pack(side=tk.LEFT, ipady=4)
        self.cbo_genre.bind("<<ComboboxSelected>>", self.on_filter_change)

        # --- 3. CHỌN NGÀY (Bên phải) ---
        f_date = tk.Frame(toolbar, bg="white", cursor="hand2")
        f_date.pack(side=tk.RIGHT)

        tk.Label(f_date, text="Ngày chiếu", bg="white", fg="#757575", font=("Arial", 9)).pack(anchor="e",
                                                                                              pady=(0, 2))

        # Khung hiển thị ngày
        date_display = tk.Frame(f_date, bg="#f5f6f8", padx=10, pady=5, highlightbackground="#bdbdbd",
                                highlightthickness=1)
        date_display.pack(anchor="e")

        lbl_icon = tk.Label(date_display, text="📅", font=("Arial", 12), bg="#f5f6f8", fg="#1976d2")
        lbl_icon.pack(side=tk.LEFT)

        self.lbl_date = tk.Label(date_display, text=self.current_date, font=("Arial", 12, "bold"), bg="#f5f6f8",
                                 fg="#333")
        self.lbl_date.pack(side=tk.LEFT, padx=(5, 0))

        # Sự kiện chọn ngày
        def open_cal(e):
            DatePickerPopup(self.parent, self.current_date, self.on_date_selected, trigger_widget=f_date)

        date_display.bind("<Button-1>", open_cal)
        self.lbl_date.bind("<Button-1>", open_cal)
        lbl_icon.bind("<Button-1>", open_cal)


    def render_scroll_area(self):
        container_scroll = tk.Frame(self.content, bg="white")
        container_scroll.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        canvas = tk.Canvas(container_scroll, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_scroll, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            try:
                # Kiểm tra xem canvas còn tồn tại không trước khi cuộn
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                # Nếu có lỗi (do widget đã bị hủy), chỉ cần bỏ qua
                pass

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ---------------------------------------------------------
    # LOGIC LOAD DỮ LIỆU
    # ---------------------------------------------------------
    def on_date_selected(self, new_date):
        self.current_date = new_date
        self.lbl_date.config(text=new_date)
        self.load_data()

    def on_filter_change(self, event):
        self.load_data()

    def load_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        keyword = self.entry_search.get().strip()
        genre = self.cbo_genre.get()

        movies_list = self.controller.get_movies_by_date(self.current_date, keyword, genre)

        if not movies_list:
            tk.Label(self.scrollable_frame, text="Không có suất chiếu nào phù hợp!",
                     bg="white", fg="#888", font=("Arial", 12)).pack(pady=20)
            return

        for item in movies_list:
            movie = item['data']
            showtimes = item['showtimes']
            self.create_movie_card(movie, showtimes)

    def create_movie_card(self, movie, showtimes):
        card = tk.Frame(self.scrollable_frame, bg="white", pady=15)
        card.pack(fill=tk.X, anchor="w")

        tk.Label(card, text=movie.title, font=("Arial", 16, "bold"), bg="white", fg="#222").pack(anchor="w")

        extra = movie.extra_info if movie.extra_info else {}
        info_text = f"{extra.get('genre', 'N/A')} - {movie.duration_min} phút"
        tk.Label(card, text=info_text, font=("Arial", 10), bg="white", fg="#666").pack(anchor="w", pady=(0, 10))

        content_row = tk.Frame(card, bg="white")
        content_row.pack(fill=tk.X, anchor="w")

        # 1. Poster
        poster_frame = tk.Frame(content_row, bg="#ddd", width=120, height=180)
        poster_frame.pack(side=tk.LEFT)
        poster_frame.pack_propagate(False)

        if movie.poster_path and os.path.exists(movie.poster_path):
            try:
                img = Image.open(movie.poster_path)
                img = img.resize((120, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(poster_frame, image=photo, bg="white")
                lbl_img.image = photo
                lbl_img.pack(fill=tk.BOTH, expand=True)
            except:
                tk.Label(poster_frame, text="POSTER", bg="#ddd", fg="#666").pack(expand=True)
        else:
            tk.Label(poster_frame, text="POSTER", bg="#ddd", fg="#666").pack(expand=True)

        # 2. Danh sách giờ chiếu
        time_frame = tk.Frame(content_row, bg="white")
        time_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True, anchor="nw")

        showtimes.sort(key=lambda x: x.start_time)

        row_container = tk.Frame(time_frame, bg="white")
        row_container.pack(anchor="w")

        count = 0
        for st in showtimes:
            time_str = st.start_time.strftime("%H:%M")

            btn = tk.Button(row_container, text=time_str, font=("Arial", 11),
                            bg="#cfd8dc", fg="#333", relief="flat", width=10, pady=6,
                            activebackground="#ff9800", activeforeground="white",
                            cursor="hand2",
                            command=lambda s_id=st.showtime_id: self.open_booking(s_id))
            btn.pack(side=tk.LEFT, padx=5, pady=5)

            count += 1
            if count % 6 == 0:
                row_container = tk.Frame(time_frame, bg="white")
                row_container.pack(anchor="w", pady=5)

    def open_booking(self, showtime_id):
        # Mở màn hình đặt vé (BookingDialog) và truyền user_id vào
        # Để lưu vào database biết ai là người bán vé
        if self.user_id:
            BookingDialog(self.parent, self.controller, showtime_id, self.user_id)
        else:
            messagebox.showerror("Lỗi", "Không xác định được nhân viên bán vé!")