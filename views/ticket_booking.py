import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
from views.date_picker_popup import DatePickerPopup
from controllers.ticket_controller import TicketController
# --- IMPORT MỚI: Dùng BookingDialog để bán vé ---
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

        # --- TÌM KIẾM ---
        f_search = tk.Frame(toolbar, bg="white")
        f_search.pack(side=tk.LEFT, padx=(0, 40))
        tk.Label(f_search, text="🔍", font=("Arial", 14), bg="white", fg="#555").pack(side=tk.LEFT)

        self.entry_search = tk.Entry(f_search, font=("Arial", 11), width=25, bd=0, bg="white")
        self.entry_search.pack(side=tk.LEFT)
        self.entry_search.bind("<KeyRelease>", self.on_filter_change)  # Gõ là lọc

        tk.Frame(f_search, bg="black", height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(f_search, text="Tìm kiếm tên phim", bg="white", fg="#999", font=("Arial", 8)).place(x=25, y=-15)

        # --- THỂ LOẠI ---
        f_genre = tk.Frame(toolbar, bg="white")
        f_genre.pack(side=tk.LEFT, padx=(0, 40))
        tk.Label(f_genre, text="▽", font=("Arial", 12), bg="white", fg="#555").pack(side=tk.LEFT)

        self.cbo_genre = ttk.Combobox(f_genre,
                                      values=["Tất cả", "Hành động", "Kinh dị", "Hoạt hình", "Tình cảm", "Hài"],
                                      font=("Arial", 11), width=15, state="readonly")
        self.cbo_genre.current(0)
        self.cbo_genre.pack(side=tk.LEFT)
        self.cbo_genre.bind("<<ComboboxSelected>>", self.on_filter_change)  # Chọn là lọc

        tk.Frame(f_genre, bg="black", height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(f_genre, text="Thể loại", bg="white", fg="#999", font=("Arial", 8)).place(x=20, y=-15)

        # --- CHỌN NGÀY ---
        f_date = tk.Frame(toolbar, bg="white", cursor="hand2")
        f_date.pack(side=tk.RIGHT)

        self.lbl_date = tk.Label(f_date, text=self.current_date, font=("Arial", 14, "bold"), bg="white", fg="#0f1746")
        self.lbl_date.pack(side=tk.LEFT, padx=10)

        lbl_icon = tk.Label(f_date, text="📅", font=("Arial", 16), bg="white", fg="#555")
        lbl_icon.pack(side=tk.LEFT)

        def open_cal(e):
            DatePickerPopup(self.parent, self.current_date, self.on_date_selected, trigger_widget=f_date)

        f_date.bind("<Button-1>", open_cal)
        self.lbl_date.bind("<Button-1>", open_cal)
        lbl_icon.bind("<Button-1>", open_cal)

        tk.Frame(f_date, bg="black", height=1).pack(side=tk.BOTTOM, fill=tk.X)

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
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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