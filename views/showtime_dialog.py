import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup
from datetime import datetime


class ShowtimeDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", st_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.st_id = st_id
        self.on_success = on_success

        self.title("Thêm suất chiếu" if mode == "add" else "Sửa suất chiếu")
        self.geometry("600x450")
        self.config(bg="#f5f6f8")
        self.grab_set()

        # Load danh sách phim và phòng để điền vào Combobox
        self.movies_list, self.rooms_list = self.controller.get_resources()

        # Mapping để lấy ID từ Tên
        self.movie_map = {m.title: m.movie_id for m in self.movies_list}
        self.room_map = {r.room_name: r.room_id for r in self.rooms_list}

        self.render_ui()

        if mode == "edit" and st_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        tk.Label(container, text=self.title(), font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # Phim
        tk.Label(container, text="Phim", bg="#f5f6f8").pack(anchor="w")
        self.cbo_movie = ttk.Combobox(container, values=list(self.movie_map.keys()), font=("Arial", 11),
                                      state="readonly")
        self.cbo_movie.pack(fill=tk.X, pady=5)

        # Phòng
        tk.Label(container, text="Phòng chiếu", bg="#f5f6f8").pack(anchor="w", pady=(10, 0))
        self.cbo_room = ttk.Combobox(container, values=list(self.room_map.keys()), font=("Arial", 11), state="readonly")
        self.cbo_room.pack(fill=tk.X, pady=5)

        # Ngày & Giờ (Trên cùng 1 hàng)
        row_time = tk.Frame(container, bg="#f5f6f8")
        row_time.pack(fill=tk.X, pady=10)

        # Ngày
        f_date = tk.Frame(row_time, bg="#f5f6f8")
        f_date.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_date, text="Ngày chiếu (dd/mm/yyyy)", bg="#f5f6f8").pack(anchor="w")
        self.e_date = tk.Entry(f_date, font=("Arial", 11))
        self.e_date.pack(fill=tk.X, ipady=3)

        # Bind lịch
        def open_cal(e):
            DatePickerPopup(self, self.e_date.get(),
                            lambda d: (self.e_date.delete(0, tk.END), self.e_date.insert(0, d)),
                            trigger_widget=self.e_date)

        self.e_date.bind("<Button-1>", open_cal)

        # Giờ
        f_time = tk.Frame(row_time, bg="#f5f6f8")
        f_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(f_time, text="Giờ chiếu (HH:MM)", bg="#f5f6f8").pack(anchor="w")
        self.e_time = tk.Entry(f_time, font=("Arial", 11))
        self.e_time.pack(fill=tk.X, ipady=3)

        # Giá vé
        tk.Label(container, text="Giá vé (VND)", bg="#f5f6f8").pack(anchor="w", pady=(10, 0))
        self.e_price = tk.Entry(container, font=("Arial", 11))
        self.e_price.pack(fill=tk.X, pady=5, ipady=3)

        # Nút Lưu
        tk.Button(container, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 11, "bold"),
                  width=15, command=self.save_action).pack(pady=30)

    def load_data(self):
        st = self.controller.get_detail(self.st_id)
        if st:
            # Set Combobox Phim
            if st.movie: self.cbo_movie.set(st.movie.title)
            # Set Combobox Phòng
            if st.room: self.cbo_room.set(st.room.room_name)
            # Set Ngày Giờ
            self.e_date.insert(0, st.start_time.strftime("%d/%m/%Y"))
            self.e_time.insert(0, st.start_time.strftime("%H:%M"))
            # Set Giá
            self.e_price.insert(0, int(st.ticket_price))

    def save_action(self):
        movie_name = self.cbo_movie.get()
        room_name = self.cbo_room.get()
        date_str = self.e_date.get()
        time_str = self.e_time.get()
        price = self.e_price.get()

        movie_id = self.movie_map.get(movie_name)
        room_id = self.room_map.get(room_name)

        success, msg = self.controller.save(self.mode, self.st_id, movie_id, room_id, date_str, time_str, price)

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)