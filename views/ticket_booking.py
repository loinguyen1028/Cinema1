import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
from views.date_picker_popup import DatePickerPopup
from controllers.ticket_controller import TicketController
from views.booking_dialog import BookingDialog


class TicketBooking:
    def __init__(self, parent_frame, user_id=None):
        self.parent = parent_frame
        self.user_id = user_id
        self.controller = TicketController()

        self.current_date = datetime.now().strftime("%d/%m/%Y")

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "btn": "#2563eb",
            "selected": "#334155"
        }

        self.render()


    def render(self):
        self.content = tk.Frame(self.parent, bg=self.colors["bg"])
        self.content.pack(fill=tk.BOTH, expand=True)

        self.render_toolbar()
        self.render_scroll_area()
        self.load_data()


    def render_toolbar(self):
        toolbar = tk.Frame(self.content, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, padx=30, pady=20)

        # -------- SEARCH --------
        f_search = tk.Frame(toolbar, bg=self.colors["bg"])
        f_search.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            f_search,
            text="Tìm kiếm phim",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 4))


        search_border = tk.Frame(
            f_search,
            bg=self.colors["panel"],
            highlightbackground=self.colors["panel"],
            highlightthickness=1
        )
        search_border.pack()


        search_inner = tk.Frame(
            search_border,
            bg=self.colors["card"]
        )
        search_inner.pack(padx=1, pady=1)


        tk.Label(
            search_inner,
            text="🔍",
            font=("Arial", 11),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(side=tk.LEFT, padx=(8, 4))


        self.entry_search = tk.Entry(
            search_inner,
            font=("Arial", 11),
            width=24,
            bd=0,
            bg=self.colors["card"],
            fg=self.colors["text"],
            insertbackground=self.colors["primary"]
        )
        self.entry_search.pack(side=tk.LEFT, ipady=7, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self.on_filter_change)


        self.entry_search.bind(
            "<FocusIn>",
            lambda e: search_border.config(
                highlightbackground=self.colors["primary"],
                highlightthickness=2
            )
        )

        self.entry_search.bind(
            "<FocusOut>",
            lambda e: search_border.config(
                highlightbackground=self.colors["panel"],
                highlightthickness=1
            )
        )


        f_genre = tk.Frame(toolbar, bg=self.colors["bg"])
        f_genre.pack(side=tk.LEFT)

        tk.Label(
            f_genre, text="Thể loại",
            bg=self.colors["bg"], fg=self.colors["muted"],
            font=("Arial", 9)
        ).pack(anchor="w", pady=(0, 2))

        style = ttk.Style()
        style.theme_use("default")

        self.cbo_genre = ttk.Combobox(
            f_genre,
            values=["Tất cả", "Hành động", "Kinh dị", "Hoạt hình", "Tình cảm", "Hài"],
            font=("Arial", 11),
            width=15,
            state="readonly"
        )
        self.cbo_genre.current(0)
        self.cbo_genre.pack(ipady=4)
        self.cbo_genre.bind("<<ComboboxSelected>>", self.on_filter_change)

        # -------- DATE --------
        f_date = tk.Frame(toolbar, bg=self.colors["bg"], cursor="hand2")
        f_date.pack(side=tk.RIGHT)

        tk.Label(
            f_date, text="Ngày chiếu",
            bg=self.colors["bg"], fg=self.colors["muted"],
            font=("Arial", 9)
        ).pack(anchor="e", pady=(0, 2))

        date_box = tk.Frame(
            f_date,
            bg=self.colors["card"],
            padx=12, pady=6,
            highlightbackground=self.colors["panel"],
            highlightthickness=1
        )
        date_box.pack(anchor="e")

        tk.Label(
            date_box, text="📅",
            font=("Arial", 12),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        self.lbl_date = tk.Label(
            date_box,
            text=self.current_date,
            font=("Arial", 12, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        )
        self.lbl_date.pack(side=tk.LEFT, padx=(5, 0))

        def open_cal(e):
            DatePickerPopup(self.parent, self.current_date, self.on_date_selected, trigger_widget=f_date)

        date_box.bind("<Button-1>", open_cal)
        self.lbl_date.bind("<Button-1>", open_cal)


    def render_scroll_area(self):
        container = tk.Frame(self.content, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        self.canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def on_date_selected(self, new_date):
        try:
            selected_dt = datetime.strptime(new_date, "%d/%m/%Y")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            if selected_dt < today:
                messagebox.showwarning("Cảnh báo", "Không thể chọn ngày trong quá khứ!")
                return
        except ValueError:
            pass

        self.current_date = new_date
        self.lbl_date.config(text=new_date)
        self.load_data()

    def on_filter_change(self, event=None):
        self.load_data()

    def load_data(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        keyword = self.entry_search.get().strip()
        genre = self.cbo_genre.get()

        movies_list = self.controller.get_movies_by_date(self.current_date, keyword, genre)

        if not movies_list:
            tk.Label(
                self.scrollable_frame,
                text="Không có suất chiếu phù hợp!",
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                font=("Arial", 12)
            ).pack(pady=20)
            return

        for item in movies_list:
            self.create_movie_card(item["data"], item["showtimes"])


    def create_movie_card(self, movie, showtimes):
        now = datetime.now()
        is_today = self.current_date == now.strftime("%d/%m/%Y")

        valid_showtimes = []
        for st in showtimes:
            st_time = st.start_time
            if isinstance(st_time, datetime):
                st_time = st_time.time()

            if is_today and st_time < now.time():
                continue

            valid_showtimes.append(st)

        if not valid_showtimes:
            return

        showtimes = valid_showtimes

        card = tk.Frame(
            self.scrollable_frame,
            bg=self.colors["card"],
            padx=15, pady=15,
            highlightbackground=self.colors["panel"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=10)

        tk.Label(
            card, text=movie.title,
            font=("Arial", 16, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(anchor="w")

        extra = movie.extra_info or {}
        info = f"{extra.get('genre', 'N/A')} - {movie.duration_min} phút"
        tk.Label(
            card, text=info,
            font=("Arial", 10),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="w", pady=(0, 10))

        row = tk.Frame(card, bg=self.colors["card"])
        row.pack(fill=tk.X)


        poster = tk.Frame(row, bg=self.colors["panel"], width=120, height=180)
        poster.pack(side=tk.LEFT)
        poster.pack_propagate(False)

        if movie.poster_path and os.path.exists(movie.poster_path):
            try:
                img = Image.open(movie.poster_path).resize((120, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(poster, image=photo, bg=self.colors["panel"])
                lbl.image = photo
                lbl.pack(fill=tk.BOTH, expand=True)
            except:
                tk.Label(poster, text="POSTER", bg=self.colors["panel"], fg=self.colors["muted"]).pack(expand=True)
        else:
            tk.Label(poster, text="POSTER", bg=self.colors["panel"], fg=self.colors["muted"]).pack(expand=True)


        time_frame = tk.Frame(row, bg=self.colors["card"])
        time_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)

        showtimes.sort(key=lambda x: x.start_time)

        line = tk.Frame(time_frame, bg=self.colors["card"])
        line.pack(anchor="w")

        count = 0
        for st in showtimes:
            btn = tk.Button(
                line,
                text=st.start_time.strftime("%H:%M"),
                font=("Arial", 11, "bold"),
                bg=self.colors["panel"],
                fg=self.colors["text"],
                relief="flat",
                width=10,
                pady=6,
                cursor="hand2",
                activebackground=self.colors["primary"],
                activeforeground="#000",
                command=lambda s=st.showtime_id: self.open_booking(s)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)

            btn.bind("<Enter>", lambda e, b=btn: b.config(
                bg=self.colors["primary"], fg="#000"
            ))
            btn.bind("<Leave>", lambda e, b=btn: b.config(
                bg=self.colors["panel"], fg=self.colors["text"]
            ))

            count += 1
            if count % 6 == 0:
                line = tk.Frame(time_frame, bg=self.colors["card"])
                line.pack(anchor="w", pady=5)


    def open_booking(self, showtime_id):
        if self.user_id:
            BookingDialog(self.parent, self.controller, showtime_id, self.user_id)
        else:
            messagebox.showerror("Lỗi", "Không xác định được nhân viên bán vé!")
