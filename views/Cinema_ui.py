import tkinter as tk
from tkinter import messagebox

from views.movie_manager import MovieManager
from views.showtime_manager import ShowtimeManager
from views.staff_manager import StaffManager
from views.customer_manager import CustomerManager
from views.room_manager import RoomManager
from views.change_password_dialog import ChangePasswordDialog
from views.product_manager import ProductManager
from views.tier_manager import TierManager
from views.stat_manager import StatManager


THEME = {
    "bg": "#0f172a",
    "panel": "#111827",
    "card": "#1f2933",
    "primary": "#facc15",
    "text": "#e5e7eb",
    "muted": "#9ca3af",
    "hover": "#0f172a",
    "border": "#374151"
}


class CinemaApp:
    def __init__(self, root, user_id=None, on_logout=None):
        self.root = root
        self.user_id = user_id
        self.on_logout = on_logout
        self.colors = THEME
        self.active_page = None

        self.root.title("LHQ Cinema - Admin")
        self.root.geometry("1300x750")

        self.sidebar_frame = tk.Frame(
            root,
            bg=self.colors["panel"],
            width=250
        )
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self.main_area = tk.Frame(root, bg=self.colors["bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_header()

        self.body_frame = tk.Frame(self.main_area, bg=self.colors["bg"])
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_data = [
            ("Quản lí phim", "🎬"),
            ("Quản lí suất chiếu", "🎞"),
            ("Quản lí phòng chiếu", "🏢"),
            ("Quản lí sản phẩm", "🥤"),
            ("Quản lí nhân sự", "👥"),
            ("Quản lí khách hàng", "👨‍👩‍👧"),
            ("Quản lí hạng", "⭐"),
            ("Thống kê", "📊"),
        ]

        self.menu_buttons = {}
        self.create_sidebar()
        self.switch_page("Quản lí phim")

    def create_header(self):
        header = tk.Frame(self.main_area, bg=self.colors["panel"], height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        user_frame = tk.Frame(header, bg=self.colors["panel"])
        user_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Label(
            user_frame,
            text="👤",
            font=("Arial", 16),
            bg=self.colors["card"],
            fg=self.colors["primary"],
            width=2
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            user_frame,
            text="Admin",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        lbl_more = tk.Label(
            user_frame,
            text="⋮",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Arial", 14, "bold"),
            cursor="hand2"
        )
        lbl_more.pack(side=tk.LEFT, padx=5)
        lbl_more.bind("<Button-1>", self.show_admin_menu)

    def show_admin_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Đổi mật khẩu", command=self.open_change_pass)
        menu.add_separator()
        menu.add_command(label="Đăng xuất", command=self.on_logout, foreground="red")
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def open_change_pass(self):
        if self.user_id:
            ChangePasswordDialog(self.root, self.user_id)
        else:
            messagebox.showerror("Lỗi", "Không xác định được tài khoản!")

    def create_sidebar(self):
        logo_frame = tk.Frame(self.sidebar_frame, bg=self.colors["panel"], height=80)
        logo_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            logo_frame,
            text="🎬",
            font=("Arial", 30),
            bg=self.colors["panel"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT, padx=(20, 5))

        tk.Label(
            logo_frame,
            text="LHQ\nCinema",
            font=("Arial", 16, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            justify=tk.LEFT
        ).pack(side=tk.LEFT)

        def on_enter(frame):
            frame.config(bg=self.colors["hover"])

        def on_leave(frame, name):
            if self.active_page != name:
                frame.config(bg=self.colors["panel"])

        for name, icon in self.menu_data:
            btn_frame = tk.Frame(
                self.sidebar_frame,
                bg=self.colors["panel"],
                cursor="hand2"
            )
            btn_frame.pack(fill=tk.X, pady=5, padx=10)

            lbl_icon = tk.Label(
                btn_frame,
                text=icon,
                bg=self.colors["panel"],
                fg=self.colors["text"],
                font=("Arial", 14)
            )
            lbl_icon.pack(side=tk.LEFT, padx=(10, 10), pady=10)

            lbl_text = tk.Label(
                btn_frame,
                text=name,
                bg=self.colors["panel"],
                fg=self.colors["text"],
                font=("Arial", 11, "bold")
            )
            lbl_text.pack(side=tk.LEFT, pady=10)

            self.menu_buttons[name] = (btn_frame, lbl_icon, lbl_text)

            for w in (btn_frame, lbl_icon, lbl_text):
                w.bind("<Button-1>", lambda e, n=name: self.switch_page(n))

            btn_frame.bind("<Enter>", lambda e, f=btn_frame: on_enter(f))
            btn_frame.bind("<Leave>", lambda e, f=btn_frame, n=name: on_leave(f, n))

    def switch_page(self, page_name):
        self.update_sidebar_visuals(page_name)

        for widget in self.body_frame.winfo_children():
            widget.destroy()

        if page_name == "Quản lí phim":
            MovieManager(self.body_frame)
        elif page_name == "Quản lí suất chiếu":
            ShowtimeManager(self.body_frame)
        elif page_name == "Quản lí phòng chiếu":
            RoomManager(self.body_frame)
        elif page_name == "Quản lí sản phẩm":
            ProductManager(self.body_frame)
        elif page_name == "Quản lí nhân sự":
            StaffManager(self.body_frame)
        elif page_name == "Quản lí khách hàng":
            CustomerManager(self.body_frame)
        elif page_name == "Quản lí hạng":
            TierManager(self.body_frame)
        elif page_name == "Thống kê":
            StatManager(self.body_frame)
        else:
            self.render_empty_page(page_name)

    def update_sidebar_visuals(self, active_page):
        self.active_page = active_page

        for name, (frame, icon, text) in self.menu_buttons.items():
            if name == active_page:
                frame.config(bg=self.colors["hover"])
                icon.config(fg=self.colors["primary"])
                text.config(fg=self.colors["primary"])
            else:
                frame.config(bg=self.colors["panel"])
                icon.config(fg=self.colors["text"])
                text.config(fg=self.colors["text"])

    def render_empty_page(self, title):
        tk.Label(
            self.body_frame,
            text=title,
            font=("Arial", 20, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["muted"]
        ).pack(expand=True)
