import tkinter as tk
from views.ticket_booking import TicketBooking  # <--- Import file mới

class StaffApp:
    def __init__(self, root, on_logout=None):
        self.root = root

        self.on_logout = on_logout

        self.root.title("LHQ Cinema - Staff (Bán vé)")
        self.root.geometry("1300x750")
        
        self.colors = {
            "sidebar_bg": "#0f1746",     
            "content_bg": "white",       
            "text_white": "#ffffff",
            "active_orange": "#ff9800"
        }
        
        # --- Layout Chính ---
        self.sidebar_frame = tk.Frame(root, bg=self.colors["sidebar_bg"], width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self.main_area = tk.Frame(root, bg=self.colors["content_bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_header()
        
        # Container cho nội dung thay đổi
        self.body_frame = tk.Frame(self.main_area, bg=self.colors["content_bg"])
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_buttons = {} # Để lưu trạng thái nút menu
        self.create_sidebar()
        
        # Mặc định vào trang Phim (Đặt vé)
        self.switch_page("Phim")

    def create_header(self):
        header = tk.Frame(self.main_area, bg=self.colors["sidebar_bg"], height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        
        user_frame = tk.Frame(header, bg=self.colors["sidebar_bg"])
        user_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(user_frame, text="👤", font=("Arial", 18), bg="white", fg="#333", width=2).pack(side=tk.LEFT, padx=10)
        tk.Label(user_frame, text="Nhân viên", bg=self.colors["sidebar_bg"], fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # 2. XỬ LÝ NÚT 3 CHẤM
        lbl_more = tk.Label(user_frame, text="⋮", bg=self.colors["sidebar_bg"], fg="white", 
                            font=("Arial", 14, "bold"), cursor="hand2")
        lbl_more.pack(side=tk.LEFT, padx=5)
        
        # Gán sự kiện click chuột trái để mở menu
        lbl_more.bind("<Button-1>", self.show_user_menu)

    def show_user_menu(self, event):
        """Hàm hiển thị Menu nhỏ (Popup) ngay tại chuột"""
        # Tạo menu
        menu = tk.Menu(self.root, tearoff=0)
        
        # Thêm các mục
        # menu.add_command(label="Thông tin tài khoản", command=lambda: print("Xem info"))
        menu.add_separator() # Đường gạch ngang
        menu.add_command(label="Đăng xuất", command=self.on_logout, foreground="red") # Gọi hàm logout từ main.py
        
        # Hiển thị menu tại vị trí con trỏ chuột (x_root, y_root)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Đảm bảo thả chuột ra menu không bị kẹt
            menu.grab_release()

    def create_sidebar(self):
        # Logo
        logo_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], height=80)
        logo_frame.pack(fill=tk.X, pady=20)
        tk.Label(logo_frame, text="🎬", font=("Arial", 30), bg=self.colors["sidebar_bg"], fg="#5c9aff").pack(side=tk.LEFT, padx=(20, 5))
        tk.Label(logo_frame, text="LHQ\nCinema", font=("Arial", 16, "bold"), bg=self.colors["sidebar_bg"], fg="white", justify=tk.LEFT).pack(side=tk.LEFT)

        # Menu Items
        menu_items = [("Phim", "🎞"), ("Đồ ăn", "🍿"), ("Vé đã đặt", "🎟")]
        
        for name, icon in menu_items:
            btn_frame = tk.Frame(self.sidebar_frame, bg=self.colors["sidebar_bg"], cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=5, padx=10)
            
            lbl_icon = tk.Label(btn_frame, text=icon, bg=self.colors["sidebar_bg"], fg="white", font=("Arial", 14))
            lbl_icon.pack(side=tk.LEFT, padx=(10, 10), pady=10)
            
            lbl_text = tk.Label(btn_frame, text=name, bg=self.colors["sidebar_bg"], fg="white", font=("Arial", 11, "bold"))
            lbl_text.pack(side=tk.LEFT, pady=10)

            # Lưu lại để đổi màu active
            self.menu_buttons[name] = (lbl_icon, lbl_text)

            # Bind sự kiện
            btn_frame.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_icon.bind("<Button-1>", lambda e, n=name: self.switch_page(n))
            lbl_text.bind("<Button-1>", lambda e, n=name: self.switch_page(n))

    def switch_page(self, page_name):
        # 1. Cập nhật màu sắc Menu
        for name, (icon, text) in self.menu_buttons.items():
            if name == page_name:
                icon.config(fg=self.colors["active_orange"])
                text.config(fg=self.colors["active_orange"])
            else:
                icon.config(fg="white")
                text.config(fg="white")

        # 2. Xóa nội dung cũ trong body_frame
        for widget in self.body_frame.winfo_children():
            widget.destroy()
            
        # 3. Load nội dung mới
        if page_name == "Phim":
            # Gọi class TicketBooking từ file ticket_booking.py
            TicketBooking(self.body_frame)
        else:
            self.render_empty_page(page_name)

    def render_empty_page(self, title):
        tk.Label(self.body_frame, text=f"Chức năng: {title}", font=("Arial", 20, "bold"), bg="white", fg="#ccc").pack(expand=True)
        tk.Label(self.body_frame, text="(Đang phát triển)", font=("Arial", 12), bg="white", fg="#ccc").pack()