import tkinter as tk
from tkinter import messagebox
from views.ticket_booking import TicketBooking
from views.customer_manager import CustomerManager
from views.change_password_dialog import ChangePasswordDialog
from views.concession_sales import ConcessionSales
from views.ticket_manager import TicketManager
from views.add_customer import AddCustomer


class StaffApp:
    def __init__(self, root, user_id=None, on_logout=None):
        self.root = root
        self.user_id = user_id
        self.on_logout = on_logout

        self.root.title("LHQ Cinema - Staff")
        self.root.geometry("1300x750")

        # 🎨 THEME VÀNG – ĐEN
        self.colors = {
            "sidebar_bg": "#0b0b0b",
            "content_bg": "#121212",
            "text_white": "#ffffff",
            "active_orange": "#f5c518",
            "hover_bg": "#1f1f1f",
            "muted_text": "#b0b0b0",
            "header_bg": "#0b0b0b"
        }

        # --- SIDEBAR ---
        self.sidebar_frame = tk.Frame(root, bg=self.colors["sidebar_bg"], width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # --- MAIN AREA ---
        self.main_area = tk.Frame(root, bg=self.colors["content_bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_header()

        self.body_frame = tk.Frame(self.main_area, bg=self.colors["content_bg"])
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_buttons = {}
        self.create_sidebar()
        self.switch_page("Phim")

    # ================= HEADER =================
    def create_header(self):
        header = tk.Frame(self.main_area, bg=self.colors["header_bg"], height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        user_frame = tk.Frame(header, bg=self.colors["header_bg"])
        user_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Label(
            user_frame,
            text="👤",
            font=("Arial", 16),
            bg="#1c1c1c",
            fg=self.colors["active_orange"],
            width=2
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            user_frame,
            text="Nhân viên",
            bg=self.colors["header_bg"],
            fg=self.colors["muted_text"],
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        lbl_more = tk.Label(
            user_frame,
            text="⋮",
            bg=self.colors["header_bg"],
            fg=self.colors["text_white"],
            font=("Arial", 14, "bold"),
            cursor="hand2"
        )
        lbl_more.pack(side=tk.LEFT, padx=5)
        lbl_more.bind("<Button-1>", self.show_user_menu)

    def show_user_menu(self, event):
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

    # ================= SIDEBAR =================
    def create_sidebar(self):
        logo_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], height=80)
        logo_frame.pack(fill=tk.X, pady=20)

        tk.Label(
            logo_frame,
            text="🎬",
            font=("Arial", 30),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["active_orange"]
        ).pack(side=tk.LEFT, padx=(20, 5))

        tk.Label(
            logo_frame,
            text="LHQ\nCinema",
            font=("Arial", 16, "bold"),
            bg=self.colors["sidebar_bg"],
            fg=self.colors["text_white"],
            justify=tk.LEFT
        ).pack(side=tk.LEFT)

        menu_items = [
            ("Phim", "🎞"),
            ("Đồ ăn", "🍿"),
            ("Vé đã đặt", "🎟"),
            ("Khách hàng", "👥")
        ]

        def on_enter(frame):
            frame.config(bg=self.colors["hover_bg"])

        def on_leave(frame):
            frame.config(bg=self.colors["sidebar_bg"])

        for name, icon in menu_items:
            btn_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=5, padx=10)

            lbl_icon = tk.Label(
                btn_frame, text=icon,
                bg=self.colors["sidebar_bg"],
                fg=self.colors["text_white"],
                font=("Arial", 14)
            )
            lbl_icon.pack(side=tk.LEFT, padx=(10, 10), pady=10)

            lbl_text = tk.Label(
                btn_frame, text=name,
                bg=self.colors["sidebar_bg"],
                fg=self.colors["text_white"],
                font=("Arial", 11, "bold")
            )
            lbl_text.pack(side=tk.LEFT, pady=10)

            self.menu_buttons[name] = (btn_frame, lbl_icon, lbl_text)

            btn_frame.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_icon.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_text.bind("<Button-1>", lambda e, n=name: self.switch_page(n))

            btn_frame.bind("<Enter>", lambda e, f=btn_frame: on_enter(f))
            btn_frame.bind("<Leave>", lambda e, f=btn_frame: on_leave(f))

    # ================= PAGE SWITCH =================
    def switch_page(self, page_name):
        for name, (frame, icon, text) in self.menu_buttons.items():
            if name == page_name:
                frame.config(bg=self.colors["hover_bg"])
                icon.config(fg=self.colors["active_orange"])
                text.config(fg=self.colors["active_orange"])
            else:
                frame.config(bg=self.colors["sidebar_bg"])
                icon.config(fg=self.colors["text_white"])
                text.config(fg=self.colors["text_white"])

        for widget in self.body_frame.winfo_children():
            widget.destroy()

        if page_name == "Phim":
            TicketBooking(self.body_frame, user_id=self.user_id)
        elif page_name == "Đồ ăn":
            ConcessionSales(self.body_frame, user_id=self.user_id)
        elif page_name == "Vé đã đặt":
            TicketManager(self.body_frame)
        elif page_name == "Khách hàng":
            AddCustomer(self.body_frame)
        else:
            self.render_empty_page(page_name)

    def render_empty_page(self, title):
        tk.Label(
            self.body_frame,
            text=title,
            font=("Arial", 20, "bold"),
            bg=self.colors["content_bg"],
            fg=self.colors["muted_text"]
        ).pack(expand=True)
