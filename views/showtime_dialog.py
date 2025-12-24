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

        # ===== STAFF THEME =====
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "input": "#0b1220"
        }

        self.title("Thêm suất chiếu" if mode == "add" else "Sửa suất chiếu")
        self.geometry("620x460")
        self.config(bg=self.colors["bg"])
        self.resizable(False, False)
        self.grab_set()

        # Load resource
        self.movies_list, self.rooms_list = self.controller.get_resources()
        self.movie_map = {m.title: m.movie_id for m in self.movies_list}
        self.room_map = {r.room_name: r.room_id for r in self.rooms_list}

        self.render_ui()

        if mode == "edit" and st_id:
            self.load_data()

    def render_ui(self):
        # ===== CARD =====
        container = tk.Frame(
            self,
            bg=self.colors["card"],
            padx=30,
            pady=25
        )
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ===== TITLE =====
        tk.Label(
            container,
            text=self.title(),
            font=("Arial", 16, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(anchor="w", pady=(0, 20))

        # ===== STYLE HELPER =====
        def label(text):
            tk.Label(
                container,
                text=text,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=("Arial", 10)
            ).pack(anchor="w")

        def entry(parent=container):
            e = tk.Entry(
                parent,
                font=("Arial", 11),
                bg=self.colors["panel"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief="flat"
            )
            e.pack(fill=tk.X, ipady=6, pady=(4, 12))
            return e

        def combo(values):
            cb = ttk.Combobox(
                container,
                values=values,
                font=("Arial", 11),
                state="readonly"
            )
            cb.pack(fill=tk.X, pady=(4, 12))
            return cb

        # ===== PHIM =====
        label("Phim")
        self.cbo_movie = combo(list(self.movie_map.keys()))

        # ===== PHÒNG =====
        label("Phòng chiếu")
        self.cbo_room = combo(list(self.room_map.keys()))

        # ===== DATE & TIME =====
        row_time = tk.Frame(container, bg=self.colors["card"])
        row_time.pack(fill=tk.X, pady=(5, 10))

        # Date
        f_date = tk.Frame(row_time, bg=self.colors["card"])
        f_date.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_date, text="Ngày chiếu (dd/mm/yyyy)", bg=self.colors["card"],
                 fg=self.colors["muted"]).pack(anchor="w")
        self.e_date = entry(f_date)

        def open_cal(e):
            DatePickerPopup(
                self,
                self.e_date.get(),
                lambda d: (self.e_date.delete(0, tk.END), self.e_date.insert(0, d)),
                trigger_widget=self.e_date
            )

        self.e_date.bind("<Button-1>", open_cal)

        # Time
        f_time = tk.Frame(row_time, bg=self.colors["card"])
        f_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(f_time, text="Giờ chiếu (HH:MM)", bg=self.colors["card"],
                 fg=self.colors["muted"]).pack(anchor="w")
        self.e_time = entry(f_time)

        # ===== PRICE =====
        label("Giá vé (VND)")
        self.e_price = entry()

        # ===== BUTTON =====
        tk.Button(
            container,
            text="💾 LƯU SUẤT CHIẾU",
            bg=self.colors["primary"],
            fg="#000000",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.save_action
        ).pack(pady=(15, 0))

    # ================= DATA =================
    def load_data(self):
        st = self.controller.get_detail(self.st_id)
        if st:
            if st.movie:
                self.cbo_movie.set(st.movie.title)
            if st.room:
                self.cbo_room.set(st.room.room_name)

            self.e_date.insert(0, st.start_time.strftime("%d/%m/%Y"))
            self.e_time.insert(0, st.start_time.strftime("%H:%M"))
            self.e_price.insert(0, int(st.ticket_price))

    # ================= SAVE =================
    def save_action(self):
        movie_name = self.cbo_movie.get()
        room_name = self.cbo_room.get()
        date_str = self.e_date.get()
        time_str = self.e_time.get()
        price = self.e_price.get()

        movie_id = self.movie_map.get(movie_name)
        room_id = self.room_map.get(room_name)

        success, msg = self.controller.save(
            self.mode,
            self.st_id,
            movie_id,
            room_id,
            date_str,
            time_str,
            price
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)
