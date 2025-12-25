import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup
from controllers.showtime_controller import ShowtimeController
from views.showtime_dialog import ShowtimeDialog
from views.showtime_detail import ShowtimeDetail
from datetime import datetime


class ShowtimeManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = ShowtimeController()

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "active": "#1e3a8a",
            "danger": "#ef4444",
            "edit": "#2563eb",
            "view": "#334155"
        }

        self.current_filter_date = datetime.now().strftime("%d/%m/%Y")
        self.current_filter_room = "Toàn bộ"

        self.action_buttons = []
        self.current_action_row = None

        self.render()

    def render(self):
        for w in self.parent.winfo_children():
            w.destroy()

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_panel = tk.Frame(container, bg=self.colors["panel"], width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        tk.Label(
            left_panel,
            text="PHÒNG CHIẾU",
            font=("Arial", 12, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["primary"]
        ).pack(anchor="w", padx=15, pady=(15, 10))

        _, rooms = self.controller.get_resources()
        room_names = ["Toàn bộ"] + [r.room_name for r in rooms]

        self.room_buttons = {}
        for r_name in room_names:
            btn = tk.Label(
                left_panel,
                text=r_name,
                font=("Arial", 11),
                bg=self.colors["panel"],
                fg=self.colors["text"],
                anchor="w",
                cursor="hand2",
                padx=15,
                pady=6
            )
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, name=r_name: self.on_select_room(name))
            self.room_buttons[r_name] = btn

        self.highlight_room_btn("Toàn bộ")

        right_panel = tk.Frame(container, bg=self.colors["bg"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(right_panel, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, pady=(0, 15))

        f_date = tk.Frame(toolbar, bg=self.colors["card"], padx=12, pady=6, cursor="hand2")
        f_date.pack(side=tk.LEFT)

        self.lbl_date = tk.Label(
            f_date,
            text=self.current_filter_date,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Arial", 11, "bold")
        )
        self.lbl_date.pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(
            f_date,
            text="📅",
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        def open_filter_cal(e):
            DatePickerPopup(
                self.parent,
                self.current_filter_date,
                self.on_date_changed,
                trigger_widget=f_date
            )

        f_date.bind("<Button-1>", open_filter_cal)
        self.lbl_date.bind("<Button-1>", open_filter_cal)

        tk.Button(
            toolbar,
            text="+ THÊM SUẤT CHIẾU",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 10, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

        table_frame = tk.Frame(right_panel, bg=self.colors["card"])
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=38,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["card"],
            foreground=self.colors["primary"],
            font=("Arial", 11, "bold")
        )

        columns = ("id", "movie", "room", "date", "time", "price", "actions")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = ["ID", "Tên phim", "Phòng", "Ngày", "Giờ", "Giá vé", "Thao tác"]
        widths = [50, 220, 90, 110, 90, 120, 170]

        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h, anchor="center")
            self.tree.column(col, width=w, anchor="center", stretch=(col != "actions"))

        self.tree.column("actions", stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_data()

    def load_data(self):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        showtimes = self.controller.get_list(
            self.current_filter_date,
            self.current_filter_room
        )

        for st in showtimes:
            self.tree.insert(
                "",
                tk.END,
                iid=st.showtime_id,
                values=(
                    st.showtime_id,
                    st.movie.title,
                    st.room.room_name,
                    st.start_time.strftime("%d/%m/%Y"),
                    st.start_time.strftime("%H:%M"),
                    f"{int(st.ticket_price):,} đ",
                    ""
                )
            )

    def create_action_buttons(self):
        base = {
            "font": ("Arial", 11),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_view = tk.Button(
            self.tree,
            text="👁",
            bg=self.colors["view"],
            fg="white",
            command=self.on_view,
            **base
        )

        self.btn_edit = tk.Button(
            self.tree,
            text="✏",
            bg=self.colors["edit"],
            fg="white",
            command=self.on_edit,
            **base
        )

        self.btn_delete = tk.Button(
            self.tree,
            text="🗑",
            bg=self.colors["danger"],
            fg="white",
            command=self.on_delete,
            **base
        )

        self.action_buttons = [self.btn_view, self.btn_edit, self.btn_delete]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        self.current_action_row = selected[0]

        bbox = self.tree.bbox(self.current_action_row, "#7")
        if not bbox:
            return

        x, y, width, height = bbox
        part = width // 3

        for i, btn in enumerate(self.action_buttons):
            btn.place(
                x=x + i * part + 4,
                y=y + 4,
                width=part - 8,
                height=height - 8
            )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    def on_view(self):
        if self.current_action_row:
            ShowtimeDetail(self.parent, self.controller, self.current_action_row)

    def on_edit(self):
        if self.current_action_row:
            self.open_dialog("edit", self.current_action_row)

    def on_delete(self):
        if not self.current_action_row:
            return

        if messagebox.askyesno("Xác nhận", "Xóa suất chiếu này?"):
            success, msg = self.controller.delete(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

    def on_select_room(self, room_name):
        self.current_filter_room = room_name
        self.highlight_room_btn(room_name)
        self.load_data()

    def highlight_room_btn(self, active_name):
        for name, btn in self.room_buttons.items():
            if name == active_name:
                btn.config(
                    bg=self.colors["active"],
                    fg=self.colors["primary"],
                    font=("Arial", 11, "bold")
                )
            else:
                btn.config(
                    bg=self.colors["panel"],
                    fg=self.colors["text"],
                    font=("Arial", 11)
                )

    def on_date_changed(self, new_date):
        self.current_filter_date = new_date
        self.lbl_date.config(text=new_date)
        self.load_data()

    def open_dialog(self, mode, st_id=None):
        ShowtimeDialog(
            self.parent,
            self.controller,
            mode,
            st_id,
            on_success=self.load_data
        )
