import tkinter as tk
from tkinter import messagebox
from views.movie_manager import MovieManager
from views.showtime_manager import ShowtimeManager
from views.staff_manager import StaffManager
from views.customer_manager import CustomerManager
from views.room_manager import RoomManager
from views.change_password_dialog import ChangePasswordDialog
from views.product_manager import ProductManager
from views.stat_manager import StatManager

class CinemaApp:
    # --- SỬA DÒNG NÀY: Thêm tham số user_id ---
    def __init__(self, root, user_id=None, on_logout=None):
        self.root = root
        self.user_id = user_id  # <--- Lưu lại user_id để dùng sau này
        self.on_logout = on_logout

        self.root.title("LHQ Cinema - Admin")
        self.root.geometry("1300x750")

        self.colors = {
            "sidebar_bg": "#0f1746",
            "content_bg": "#f0f2f5",
            "text_white": "#ffffff",
            "active_orange": "#ff9800",
            "header_bg": "#0f1746"
        }

        self.sidebar_frame = tk.Frame(root, bg=self.colors["sidebar_bg"], width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self.main_area = tk.Frame(root, bg=self.colors["content_bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_header()

        self.body_frame = tk.Frame(self.main_area, bg=self.colors["content_bg"])
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_data = [
            ("Quản lí phim", "🎬"),
            ("Quản lí suất chiếu", "🎞"),
            ("Quản lí phòng chiếu", "🏢"),
            ("Quản lí sản phẩm", "🥤"),
            ("Quản lí nhân sự", "👥"),
            ("Quản lí khách hàng", "👨‍👩‍👧"),
            ("Thống kê", "📊"),
        ]

        self.menu_buttons = {}
        self.create_sidebar()
        self.switch_page("Quản lí phim")

    def create_header(self):
        header = tk.Frame(self.main_area, bg=self.colors["header_bg"], height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        user_frame = tk.Frame(header, bg=self.colors["header_bg"])
        user_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Label(user_frame, text="👤", font=("Arial", 18), bg="white", fg="#333", width=2).pack(side=tk.LEFT, padx=10)
        tk.Label(user_frame, text="Admin", bg=self.colors["header_bg"], fg="white", font=("Arial", 10)).pack(
            side=tk.LEFT, padx=5)

        lbl_more = tk.Label(user_frame, text="⋮", bg=self.colors["header_bg"], fg="white",
                            font=("Arial", 14, "bold"), cursor="hand2")
        lbl_more.pack(side=tk.LEFT, padx=5)
        lbl_more.bind("<Button-1>", self.show_admin_menu)

    def show_admin_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        # Gán lệnh mở dialog đổi mật khẩu
        menu.add_command(label="Đổi mật khẩu", command=self.open_change_pass)
        menu.add_separator()
        menu.add_command(label="Đăng xuất", command=self.on_logout, foreground="red")
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # --- HÀM MỚI: MỞ DIALOG ĐỔI MẬT KHẨU ---
    def open_change_pass(self):
        if self.user_id:
            # Truyền user_id vào dialog
            ChangePasswordDialog(self.root, self.user_id)
        else:
            messagebox.showerror("Lỗi", "Không xác định được tài khoản người dùng!")

    def create_sidebar(self):
        # (Giữ nguyên code cũ của bạn)
        logo_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], height=80)
        logo_frame.pack(fill=tk.X, pady=20)
        tk.Label(logo_frame, text="🎬", font=("Arial", 30), bg=self.colors["sidebar_bg"], fg="#5c9aff").pack(
            side=tk.LEFT, padx=(20, 5))
        tk.Label(logo_frame, text="LHQ\nCinema", font=("Arial", 16, "bold"), bg=self.colors["sidebar_bg"], fg="white",
                 justify=tk.LEFT).pack(side=tk.LEFT)

        for name, icon in self.menu_data:
            btn_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=5, padx=10)

            lbl_icon = tk.Label(btn_frame, text=icon, bg=self.colors["sidebar_bg"], fg="white", font=("Arial", 14))
            lbl_icon.pack(side=tk.LEFT, padx=(10, 10), pady=10)
            lbl_text = tk.Label(btn_frame, text=name, bg=self.colors["sidebar_bg"], fg="white",
                                font=("Arial", 11, "bold"))
            lbl_text.pack(side=tk.LEFT, pady=10)

            self.menu_buttons[name] = (btn_frame, lbl_icon, lbl_text)
            btn_frame.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_icon.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_text.bind("<Button-1>", lambda e, n=name: self.switch_page(n))

    def switch_page(self, page_name):
        # (Giữ nguyên code cũ của bạn)
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
        elif page_name == "Thống kê":
            StatManager(self.body_frame)
        else:
            self.render_empty_page(page_name)

    def update_sidebar_visuals(self, active_page):
        # (Giữ nguyên code cũ)
        for name, (frame, icon, text) in self.menu_buttons.items():
            if name == active_page:
                icon.config(fg=self.colors["active_orange"])
                text.config(fg=self.colors["active_orange"])
            else:
                icon.config(fg=self.colors["text_white"])
                text.config(fg=self.colors["text_white"])

    def render_empty_page(self, title):
        tk.Label(self.body_frame, text=f"Giao diện: {title}", font=("Arial", 20, "bold"),
                 bg=self.colors["content_bg"], fg="#333").pack(expand=True)
        tk.Label(self.body_frame, text="(Chức năng đang phát triển)", font=("Arial", 12),
                 bg=self.colors["content_bg"], fg="#666").pack(expand=True)