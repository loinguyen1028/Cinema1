import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar  # <--- Cần cài: pip install tkcalendar
from datetime import datetime
from views.date_picker_popup import DatePickerPopup

class TicketBooking:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.colors = {
            "active_orange": "#ff9800",
            "btn_default": "#cfd8dc",
            "text_primary": "#333",
            "text_secondary": "#666"
        }
        
        # Dữ liệu gốc (Mock data)
        # Cấu trúc: (Tên phim, Thể loại, [Giờ chiếu], Poster Color/Path)
        self.all_movies = [
            ("Quỷ ăn tạng", "Kinh dị", ["15:30", "19:30", "21:00", "23:15"], "#333"),
            ("Phi vụ động trời 2", "Hoạt hình", ["09:00", "14:15", "19:30"], "#444"),
            ("Mai", "Tâm lý", ["10:30", "13:00", "16:20", "20:00"], "#555"),
            ("Đào, Phở và Piano", "Lịch sử", ["08:00", "18:00"], "#666"),
            ("Dune: Hành tinh cát", "Viễn tưởng", ["09:30", "15:00", "20:30"], "#777"),
        ]
        
        # Biến lưu trạng thái lọc
        self.filter_name = ""
        self.filter_genre = "Tất cả"
        self.selected_date = datetime.now().strftime("%d/%m/%Y") # Mặc định hôm nay

        self.render()

    def render(self):
        self.content = tk.Frame(self.parent, bg="white")
        self.content.pack(fill=tk.BOTH, expand=True)

        # 1. Render Toolbar (Tìm kiếm, Filter, Lịch)
        self.render_toolbar()

        # 2. Render Khu vực danh sách phim
        self.render_movie_list_area()

        # 3. Load dữ liệu lần đầu
        self.refresh_movie_list()

    def render_toolbar(self):
        toolbar = tk.Frame(self.content, bg="white")
        toolbar.pack(fill=tk.X, padx=30, pady=20)

        # --- 1. TÌM KIẾM (SEARCH) ---
        f_search = tk.Frame(toolbar, bg="white")
        f_search.pack(side=tk.LEFT, padx=(0, 50)) # Cách đoạn kế tiếp 50px

        # Icon kính lúp
        tk.Label(f_search, text="🔍", font=("Arial", 14), bg="white", fg="#555").pack(side=tk.LEFT, padx=(0, 5))
        
        # Container chứa Entry và đường kẻ
        input_container = tk.Frame(f_search, bg="white")
        input_container.pack(side=tk.LEFT)

        # Entry: Tắt viền (bd=0), tắt highlight khi focus
        self.entry_search = tk.Entry(input_container, font=("Arial", 11), width=30, 
                                     bd=0, highlightthickness=0, bg="white")
        self.entry_search.pack(fill=tk.X)
        self.entry_search.bind("<KeyRelease>", self.on_search_change)
        
        # Đường gạch chân (Dùng Frame chiều cao 2px)
        # Bạn có thể đổi bg="black" thành màu xanh "#0f1746" nếu thích
        underline = tk.Frame(input_container, bg="#333", height=2) 
        underline.pack(fill=tk.X, pady=(2, 0)) # pady=2 để cách chữ ra một chút

        # Label "Tìm kiếm" nhỏ nhỏ nằm phía trên (như thiết kế Material)
        # Dùng place để đặt nó lơ lửng
        lbl_placeholder = tk.Label(input_container, text="Tìm kiếm tên phim", 
                                   bg="white", fg="#999", font=("Arial", 8))
        lbl_placeholder.place(x=0, y=-15)

        # Entry nhập tên phim
        self.entry_search = tk.Entry(f_search, font=("Arial", 11), width=25, bd=0, bg="white")
        self.entry_search.pack(side=tk.LEFT)
        self.entry_search.bind("<KeyRelease>", self.on_search_change) # Gõ đến đâu lọc đến đó

        # --- 2. LỌC THỂ LOẠI (FILTER) ---
        f_filter = tk.Frame(toolbar, bg="white")
        f_filter.pack(side=tk.LEFT, padx=(0, 50))

        tk.Label(f_filter, text="Lọc", font=("Arial", 12), bg="white", fg="#555").pack(side=tk.LEFT, padx=(0, 5))
        
        # Combobox chọn thể loại
        self.cbo_genre = ttk.Combobox(f_filter, values=["Tất cả", "Kinh dị", "Hoạt hình", "Tâm lý", "Lịch sử", "Viễn tưởng"], 
                                      font=("Arial", 11), width=20, state="readonly")
        self.cbo_genre.current(0)
        self.cbo_genre.pack(side=tk.LEFT)
        self.cbo_genre.bind("<<ComboboxSelected>>", self.on_genre_change)

        # Style line
        tk.Frame(f_filter, bg="black", height=1).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(f_filter, text="Thể loại", bg="white", fg="#999", font=("Arial", 9)).place(x=30, y=-18)


        # --- 3. CHỌN NGÀY (DATE PICKER) ---
        f_date = tk.Frame(toolbar, bg="white", cursor="hand2")
        f_date.pack(side=tk.RIGHT)
        
        # Label hiển thị ngày đang chọn
        self.lbl_date = tk.Label(f_date, text=self.selected_date, font=("Arial", 12, "bold"), bg="white", fg="#333")
        self.lbl_date.pack(side=tk.LEFT, padx=10)

        # Icon lịch
        lbl_icon_date = tk.Label(f_date, text="📅", font=("Arial", 16), bg="white", fg="#555")
        lbl_icon_date.pack(side=tk.LEFT)

        # Sự kiện: Bấm vào icon hoặc ngày -> Mở lịch
        f_date.bind("<Button-1>", self.open_calendar)
        self.lbl_date.bind("<Button-1>", self.open_calendar)
        lbl_icon_date.bind("<Button-1>", self.open_calendar)

        tk.Frame(f_date, bg="black", height=1).pack(side=tk.BOTTOM, fill=tk.X)

    def render_movie_list_area(self):
        # Tạo khung có thanh cuộn (Scrollable Frame)
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

    # ----------------------------------------------------------------
    # LOGIC XỬ LÝ (FILTER & DATA)
    # ----------------------------------------------------------------
    
    def on_search_change(self, event):
        self.filter_name = self.entry_search.get().lower()
        self.refresh_movie_list()

    def on_genre_change(self, event):
        self.filter_genre = self.cbo_genre.get()
        self.refresh_movie_list()

    # ... (Các đoạn code khác giữ nguyên) ...

    # --- SỬA ĐOẠN NÀY ---
    def open_calendar(self, event):
        """Gọi class popup lịch từ file riêng"""
        # Gọi DatePickerPopup và truyền hàm 'self.on_date_selected' vào để nhận kết quả
        DatePickerPopup(self.parent, self.selected_date, self.on_date_selected)

    def on_date_selected(self, new_date):
        """Hàm này sẽ tự động chạy khi bên Popup bấm 'Chọn'"""
        # 1. Cập nhật biến dữ liệu
        self.selected_date = new_date
        
        # 2. Cập nhật giao diện (Label ngày)
        self.lbl_date.config(text=new_date)
        
        # 3. Lọc lại danh sách phim theo ngày mới
        self.refresh_movie_list()
        
        # (Optional) Log kiểm tra
        # print(f"Đã cập nhật ngày mới: {new_date}")
        
    def refresh_movie_list(self):
        """Hàm lọc và vẽ lại danh sách phim"""
        # 1. Xóa danh sách cũ
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 2. Lọc dữ liệu
        filtered_movies = []
        for movie in self.all_movies:
            title, genre, times, color = movie
            
            # Điều kiện 1: Tên phim
            if self.filter_name not in title.lower():
                continue
            
            # Điều kiện 2: Thể loại
            if self.filter_genre != "Tất cả" and self.filter_genre not in genre:
                continue

            # Điều kiện 3: Ngày chiếu (Giả lập: Ngày chẵn chiếu phim chẵn, lẻ chiếu lẻ để test)
            # Trong thực tế bạn sẽ query DB: SELECT * FROM shows WHERE date = selected_date
            # Ở đây tôi giả bộ: Nếu chọn ngày khác ngày hôm nay thì đổi giờ chiếu tí cho vui
            display_times = times
            if int(self.selected_date.split('/')[0]) % 2 == 0: 
                # Nếu ngày chẵn, giả bộ thêm 1 suất chiếu
                display_times = times + ["23:59"]
            
            filtered_movies.append((title, genre, display_times, color))

        # 3. Vẽ lại
        if not filtered_movies:
            tk.Label(self.scrollable_frame, text="Không tìm thấy phim phù hợp!", bg="white", fg="#888", font=("Arial", 12)).pack(pady=20)
        else:
            for m in filtered_movies:
                self.create_movie_item(m[0], m[1], m[2], m[3])

    def create_movie_item(self, title, genre, times, color_code):
        card = tk.Frame(self.scrollable_frame, bg="white", pady=15)
        card.pack(fill=tk.X, anchor="w")

        # Tiêu đề
        tk.Label(card, text=title, font=("Arial", 16, "bold"), bg="white", fg="#222").pack(anchor="w")
        tk.Label(card, text=genre, font=("Arial", 10), bg="white", fg="#666").pack(anchor="w", pady=(0, 10))

        content_row = tk.Frame(card, bg="white")
        content_row.pack(fill=tk.X, anchor="w")

        # Poster
        poster = tk.Frame(content_row, bg=color_code, width=150, height=220)
        poster.pack(side=tk.LEFT)
        poster.pack_propagate(False)
        tk.Label(poster, text="POSTER", fg="white", bg=color_code, font=("Arial", 10, "bold")).pack(expand=True)

        # Giờ chiếu
        time_frame = tk.Frame(content_row, bg="white")
        time_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y, anchor="nw")

        for time_str in times:
            btn = tk.Button(time_frame, text=time_str, font=("Arial", 11), 
                            bg=self.colors["btn_default"], fg="#333", relief="flat", width=10, pady=6,
                            activebackground=self.colors["active_orange"], activeforeground="white",
                            cursor="hand2",
                            command=lambda t=title, h=time_str: self.on_select_showtime(t, h))
            btn.pack(side=tk.LEFT, padx=5, anchor="n")

    def on_select_showtime(self, movie, time):
        messagebox.showinfo("Đặt vé", f"Xác nhận chọn:\n\nPhim: {movie}\nNgày: {self.selected_date}\nSuất: {time}")