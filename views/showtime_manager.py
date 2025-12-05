import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup
from controllers.showtime_controller import ShowtimeController
from views.showtime_dialog import ShowtimeDialog  # Import Dialog
from views.showtime_detail import ShowtimeDetail  # Import Detail
from datetime import datetime


class ShowtimeManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = ShowtimeController()

        # Mặc định lọc theo ngày hôm nay
        self.current_filter_date = datetime.now().strftime("%d/%m/%Y")
        self.current_filter_room = "Toàn bộ"

        self.render()

    def render(self):
        container = tk.Frame(self.parent, bg="#f0f2f5")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- PANEL TRÁI (LỌC THEO PHÒNG) ---
        left_panel = tk.Frame(container, bg="#f0f2f5", width=180)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        tk.Label(left_panel, text="DANH SÁCH RẠP", font=("Arial", 12, "bold"), bg="#f0f2f5", fg="#0f1746").pack(
            anchor="w", pady=(0, 10))

        # Tạo danh sách phòng động từ DB
        _, rooms = self.controller.get_resources()
        room_names = ["Toàn bộ"] + [r.room_name for r in rooms]

        self.room_buttons = {}
        for r_name in room_names:
            btn = tk.Label(left_panel, text=r_name, font=("Arial", 11), bg="#f0f2f5", fg="#333", anchor="w",
                           cursor="hand2", padx=10, pady=5)
            btn.pack(fill=tk.X, pady=2)
            btn.bind("<Button-1>", lambda e, name=r_name: self.on_select_room(name))
            self.room_buttons[r_name] = btn

        # Highlight mặc định
        self.highlight_room_btn("Toàn bộ")

        # --- PANEL PHẢI (MAIN CONTENT) ---
        right_panel = tk.Frame(container, bg="#f0f2f5")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 1. Toolbar (Lọc Ngày + Nút Thêm)
        toolbar = tk.Frame(right_panel, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 15))

        # Bộ lọc ngày
        f_date = tk.Frame(toolbar, bg="white", padx=10, pady=5, cursor="hand2")
        f_date.pack(side=tk.LEFT)
        self.lbl_date = tk.Label(f_date, text=self.current_filter_date, bg="white", font=("Arial", 11, "bold"))
        self.lbl_date.pack(side=tk.LEFT, padx=5)
        tk.Label(f_date, text="▼", bg="white").pack(side=tk.LEFT)

        def open_filter_cal(e):
            DatePickerPopup(self.parent, self.current_filter_date, self.on_date_changed, trigger_widget=f_date)

        f_date.bind("<Button-1>", open_filter_cal)
        self.lbl_date.bind("<Button-1>", open_filter_cal)

        # Nút Thêm
        tk.Button(toolbar, text="+ Thêm Suất Chiếu", bg="#5c6bc0", fg="white", font=("Arial", 10, "bold"),
                  padx=15, relief="flat", command=lambda: self.open_dialog("add")).pack(side=tk.RIGHT)

        # 2. Bảng dữ liệu
        table_frame = tk.Frame(right_panel, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "movie", "room", "date", "time", "price", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["ID", "Tên phim", "Phòng chiếu", "Ngày", "Giờ", "Giá vé", "Thao tác"]
        widths = [40, 200, 80, 100, 80, 100, 150]

        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h, anchor="w")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.heading("actions", anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        self.load_data()

    # --- LOGIC ---
    def load_data(self):
        # Gọi Controller lọc theo Ngày và Phòng hiện tại
        showtimes = self.controller.get_list(self.current_filter_date, self.current_filter_room)
        self.update_table(showtimes)

    def update_table(self, showtimes):
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_btns = "👁       ✏       🗑"
        for st in showtimes:
            # Format dữ liệu hiển thị
            d_str = st.start_time.strftime("%d/%m/%Y")
            t_str = st.start_time.strftime("%H:%M")
            price_str = f"{int(st.ticket_price):,}"

            vals = (st.showtime_id, st.movie.title, st.room.room_name, d_str, t_str, price_str, action_btns)
            self.tree.insert("", tk.END, iid=st.showtime_id, values=vals)

    def on_select_room(self, room_name):
        self.current_filter_room = room_name
        self.highlight_room_btn(room_name)
        self.load_data()  # Reload lại bảng

    def highlight_room_btn(self, active_name):
        for name, btn in self.room_buttons.items():
            if name == active_name:
                btn.config(bg="#e3f2fd", fg="#1976d2", font=("Arial", 11, "bold"))
            else:
                btn.config(bg="#f0f2f5", fg="#333", font=("Arial", 11, "normal"))

    def on_date_changed(self, new_date):
        self.current_filter_date = new_date
        self.lbl_date.config(text=new_date)
        self.load_data()

    def open_dialog(self, mode, st_id=None):
        ShowtimeDialog(self.parent, self.controller, mode, st_id, on_success=self.load_data)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)

        if column == '#7':  # Cột actions
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            bbox = self.tree.bbox(item_id, column)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                rel_x = event.x - cell_x
                w = cell_width / 3

                if rel_x < w:  # Xem
                    ShowtimeDetail(self.parent, self.controller, item_id)
                elif rel_x < w * 2:  # Sửa
                    self.open_dialog("edit", item_id)
                else:  # Xóa
                    if messagebox.askyesno("Xác nhận", "Xóa suất chiếu này?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()
                        else:
                            messagebox.showerror("Lỗi", msg)