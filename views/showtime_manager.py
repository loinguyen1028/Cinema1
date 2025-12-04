import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from views.date_picker_popup import DatePickerPopup # <--- Import file lịch

class ShowtimeManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        # Ngày lọc mặc định
        self.current_filter_date = "25/12/2025" 
        self.render()

    def render(self):
        container = tk.Frame(self.parent, bg="#f0f2f5")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- PANEL TRÁI ---
        left_panel = tk.Frame(container, bg="#f0f2f5", width=150)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        tk.Label(left_panel, text="Toàn bộ", font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#ff9800", anchor="w").pack(fill=tk.X, pady=5)
        
        rooms = ["Phòng 1", "Phòng 2", "Phòng 3", "Phòng VIP"]
        for room in rooms:
            tk.Label(left_panel, text=room, font=("Arial", 11), bg="#f0f2f5", fg="#333", anchor="w", cursor="hand2").pack(fill=tk.X, pady=5)

        # --- PANEL PHẢI ---
        right_panel = tk.Frame(container, bg="#f0f2f5")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 1. Toolbar
        toolbar = tk.Frame(right_panel, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 15))

        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        tk.Entry(search_frame, width=30, font=("Arial", 11)).pack(side=tk.LEFT, ipady=3)
        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # --- DATE PICKER TRÊN TOOLBAR ---
        date_frame = tk.Frame(toolbar, bg="white", highlightbackground="#ccc", highlightthickness=1, cursor="hand2")
        date_frame.pack(side=tk.RIGHT, padx=10, ipady=2)
        
        # Lưu label vào biến instance để update sau này
        self.lbl_date = tk.Label(date_frame, text=self.current_filter_date, bg="white", font=("Arial", 10))
        self.lbl_date.pack(side=tk.LEFT, padx=5)
        
        lbl_icon = tk.Label(date_frame, text="📅", bg="white")
        lbl_icon.pack(side=tk.LEFT, padx=5)

        # Hàm mở lịch cho Toolbar
        def open_filter_date(e):
            DatePickerPopup(self.parent, self.current_filter_date, self.on_filter_date_change)
            
        # Bind sự kiện
        date_frame.bind("<Button-1>", open_filter_date)
        self.lbl_date.bind("<Button-1>", open_filter_date)
        lbl_icon.bind("<Button-1>", open_filter_date)

        # Nút Thêm
        btn_add = tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white", font=("Arial", 10, "bold"), 
                            padx=15, relief="flat", command=self.open_add_dialog)
        btn_add.pack(side=tk.RIGHT)

        # 2. Bảng dữ liệu
        table_frame = tk.Frame(right_panel, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "genre", "country", "duration", "showtimes", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["Tên phim", "Thể loại", "Quốc gia", "Thời lượng", "Giờ chiếu", ""]
        widths = [200, 100, 80, 80, 150, 50]

        for col, header, w in zip(columns, headers, widths):
            self.tree.heading(col, text=header, anchor="w" if col != "actions" else "center")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.action_icons = "✏  🗑"
        
        data = [
            (1, "Quỷ ăn tạng", "Kinh dị", "Thái", "200", "19:20, 21:30, 1:00"),
            (2, "Nobita và đảo giấu vàng", "Hoạt hình", "Nhật", "112", "09:00, 14:00"),
        ]
        for item in data:
            display_values = item[1:] + (self.action_icons,)
            self.tree.insert("", tk.END, values=display_values)

        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

    def on_filter_date_change(self, new_date):
        # Callback khi chọn ngày trên Toolbar
        self.current_filter_date = new_date
        self.lbl_date.config(text=new_date)
        # TODO: Reload lại dữ liệu bảng theo ngày mới tại đây

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        if self.tree.identify_column(event.x) == '#6': 
            item_id = self.tree.identify_row(event.y)
            values = self.tree.item(item_id, "values")
            self.open_edit_dialog(values)

    # ---------------------------------------------------------
    # DIALOG THÊM SUẤT CHIẾU (Có lịch)
    # ---------------------------------------------------------
    def open_add_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Thêm suất chiếu")
        dialog.geometry("600x400")
        dialog.config(bg="#f5f6f8")
        dialog.grab_set()

        padding_frame = tk.Frame(dialog, bg="#f5f6f8")
        padding_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        row1 = tk.Frame(padding_frame, bg="#f5f6f8")
        row1.pack(fill=tk.X, pady=5)
        
        # Tên phim
        tk.Label(row1, text="Tên phim", bg="#f5f6f8", fg="#555").grid(row=0, column=0, sticky="w")
        cbo_film = ttk.Combobox(row1, values=["Nobita và đảo giấu vàng", "Quỷ ăn tạng"], width=30, font=("Arial", 11))
        cbo_film.current(0)
        cbo_film.grid(row=1, column=0, sticky="w", padx=(0, 20), ipady=3)

        # --- NGÀY CHIẾU (Có lịch) ---
        tk.Label(row1, text="Ngày chiếu", bg="#f5f6f8", fg="#555").grid(row=0, column=1, sticky="w")
        
        date_entry = tk.Entry(row1, font=("Arial", 11), width=15)
        date_entry.insert(0, "30/12/2021")
        date_entry.grid(row=1, column=1, sticky="w", ipady=3)
        
        # Hàm mở lịch cho Dialog
        def open_dialog_cal(e):
             DatePickerPopup(dialog, date_entry.get(), lambda d: (date_entry.delete(0, tk.END), date_entry.insert(0, d)))

        date_entry.bind("<Button-1>", open_dialog_cal) # Click vào là mở lịch

        # ... (Phần còn lại giữ nguyên) ...
        row2 = tk.Frame(padding_frame, bg="#f5f6f8")
        row2.pack(fill=tk.X, pady=15)

        f1 = tk.Frame(row2, bg="#f5f6f8")
        f1.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(f1, text="Suất chiếu", bg="#f5f6f8", fg="#555").pack(anchor="w")
        tk.Entry(f1, font=("Arial", 11), width=10).pack(ipady=3)

        f2 = tk.Frame(row2, bg="#f5f6f8")
        f2.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(f2, text="Phòng chiếu", bg="#f5f6f8", fg="#555").pack(anchor="w")
        cbo_room = ttk.Combobox(f2, values=["2", "1", "3"], width=10, font=("Arial", 11))
        cbo_room.current(0)
        cbo_room.pack(ipady=3)

        f3 = tk.Frame(row2, bg="#f5f6f8")
        f3.pack(side=tk.LEFT)
        tk.Label(f3, text="Giá vé", bg="#f5f6f8", fg="#555").pack(anchor="w")
        entry_price = tk.Entry(f3, font=("Arial", 11), width=15)
        entry_price.insert(0, "45000")
        entry_price.pack(ipady=3)

        lbl_desc = tk.LabelFrame(padding_frame, text="Mô tả", bg="#f5f6f8", fg="#333", font=("Arial", 10, "bold"))
        lbl_desc.pack(fill=tk.BOTH, expand=True, pady=10)
        
        preview_text = "Nobita và đảo giấu vàng\n\nNgày chiếu: 30/12/2021\nGiờ chiếu: 19:30:00 -> 21:19:00\nPhòng chiếu: 2\nGiá vé: 45000 VND"
        tk.Label(lbl_desc, text=preview_text, bg="#f5f6f8", justify=tk.LEFT, anchor="nw", padx=10, pady=10).pack(fill=tk.BOTH, expand=True)

        btn_save = tk.Button(padding_frame, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), 
                             width=10, relief="flat", command=dialog.destroy)
        btn_save.pack(side=tk.RIGHT, pady=10)

    # ---------------------------------------------------------
    # DIALOG SỬA (Giữ nguyên phần hiển thị, chưa cần lịch ở đây vì nó là View only)
    # ---------------------------------------------------------
    def open_edit_dialog(self, values):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Chi tiết suất chiếu")
        dialog.geometry("1100x600")
        dialog.config(bg="#f0f2f5")
        dialog.grab_set()

        main_paned = tk.PanedWindow(dialog, orient=tk.HORIZONTAL, bg="#f0f2f5", sashwidth=5)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_paned, bg="#f0f2f5", width=300)
        main_paned.add(left_frame)

        tk.Label(left_frame, text="Chi tiết suất chiếu", font=("Arial", 14, "bold"), bg="#e0e0e0", anchor="w", padx=10, pady=10).pack(fill=tk.X)
        info_box = tk.Frame(left_frame, bg="#f0f2f5", padx=20, pady=20)
        info_box.pack(fill=tk.BOTH, expand=True)

        tk.Label(info_box, text="Tên phim", font=("Arial", 10, "bold"), bg="#f0f2f5").pack(anchor="w")
        tk.Label(info_box, text=values[0], font=("Arial", 12), bg="#f0f2f5").pack(anchor="w", pady=(0, 10))

        tk.Label(info_box, text="Ngày chiếu", font=("Arial", 10, "bold"), bg="#f0f2f5").pack(anchor="w")
        tk.Label(info_box, text="30-12-2021", font=("Arial", 12), bg="#f0f2f5").pack(anchor="w", pady=(0, 10))

        tk.Label(info_box, text="Phòng chiếu", font=("Arial", 10, "bold"), bg="#f0f2f5").pack(anchor="w")
        tk.Label(info_box, text="Phòng: 2", font=("Arial", 12), bg="#f0f2f5").pack(anchor="w", pady=(0, 10))

        price_frame = tk.Frame(info_box, bg="#f0f2f5")
        price_frame.pack(anchor="w", fill=tk.X, pady=(0, 10))
        tk.Label(price_frame, text="Giá vé", font=("Arial", 10, "bold"), bg="#f0f2f5").pack(anchor="w")
        
        pf_inner = tk.Frame(price_frame, bg="#f0f2f5")
        pf_inner.pack(anchor="w")
        tk.Label(pf_inner, text="45000", font=("Arial", 12), bg="#f0f2f5", fg="#666").pack(side=tk.LEFT)
        tk.Label(pf_inner, text="Thay đổi", font=("Arial", 10), bg="#f0f2f5", fg="#5c9aff", cursor="hand2").pack(side=tk.LEFT, padx=10)

        tk.Label(info_box, text="Các suất chiếu", font=("Arial", 10, "bold"), bg="#f0f2f5").pack(anchor="w", pady=(10, 5))
        time_frame = tk.Frame(info_box, bg="#f0f2f5")
        time_frame.pack(anchor="w")
        
        tk.Button(time_frame, text="15:30:00", bg="white", fg="black", relief="solid", bd=1, padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(time_frame, text="19:30:00", bg="#ffebee", fg="#d32f2f", relief="solid", bd=1, padx=10, pady=5).pack(side=tk.LEFT)

        btn_footer = tk.Frame(left_frame, bg="#f0f2f5", pady=20, padx=20)
        btn_footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(btn_footer, text="Xoá", bg="#ff5722", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20, pady=5).pack(side=tk.LEFT)
        tk.Button(btn_footer, text="Thoát", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20, pady=5, command=dialog.destroy).pack(side=tk.RIGHT)

        right_frame = tk.Frame(main_paned, bg="#f0f2f5")
        main_paned.add(right_frame)

        tk.Label(right_frame, text="Danh sách ghế", font=("Arial", 14, "bold"), bg="#e0e0e0", anchor="w", padx=10, pady=10).pack(fill=tk.X)

        stats_frame = tk.Frame(right_frame, bg="#f0f2f5", pady=10)
        stats_frame.pack(fill=tk.X)
        tk.Label(stats_frame, text="Tổng số ghế: 128", bg="#f0f2f5", fg="#555").pack(side=tk.LEFT, expand=True)
        tk.Label(stats_frame, text="Đã đặt: 0", bg="#f0f2f5", fg="#555").pack(side=tk.LEFT, expand=True)
        tk.Label(stats_frame, text="Còn trống: 128", bg="#f0f2f5", fg="#555").pack(side=tk.LEFT, expand=True)

        seat_container = tk.Frame(right_frame, bg="#f0f2f5")
        seat_container.pack(expand=True, padx=20, pady=20)

        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for r_idx, row_char in enumerate(rows):
            for c_idx in range(1, 17): 
                seat_name = f"{row_char}{c_idx}"
                btn = tk.Button(seat_container, text=seat_name, font=("Arial", 7), width=4, 
                                bg="white", fg="green", 
                                activebackground="green", activeforeground="white",
                                relief="solid", bd=1)
                btn.grid(row=r_idx, column=c_idx-1, padx=2, pady=2)