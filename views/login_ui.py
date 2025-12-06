import tkinter as tk
from tkinter import messagebox
from dao.auth_dao import AuthDAO
from controllers.auth_controller import AuthController

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_success = on_login_success  # Hàm callback (launch_app bên main.py)

        # Khởi tạo DAO
        self.auth_dao = AuthDAO()
        self.controller = AuthController()

        self.root.title("Đăng nhập - LHQ Cinema")
        self.root.geometry("900x600")
        self.root.config(bg="#0f1746")

        self.render_ui()

    def render_ui(self):
        self.login_frame = tk.Frame(self.root, bg="white", width=400, height=500)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)

        tk.Label(self.login_frame, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), bg="white", fg="#0f1746").pack(
            pady=(50, 10))
        tk.Label(self.login_frame, text="Hệ thống quản lý rạp chiếu phim", font=("Arial", 10), bg="white",
                 fg="#666").pack(pady=(0, 30))

        # Username
        tk.Label(self.login_frame, text="Tài khoản", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.entry_user = tk.Entry(self.login_frame, font=("Arial", 12), bd=1, relief="solid")
        self.entry_user.pack(fill=tk.X, padx=40, pady=5, ipady=5)

        # Password
        tk.Label(self.login_frame, text="Mật khẩu", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=40,
                                                                                                 pady=(10, 0))
        self.entry_pass = tk.Entry(self.login_frame, font=("Arial", 12), bd=1, relief="solid", show="*")
        self.entry_pass.pack(fill=tk.X, padx=40, pady=5, ipady=5)

        # Button Login
        tk.Button(self.login_frame, text="ĐĂNG NHẬP", bg="#ff9800", fg="white", font=("Arial", 11, "bold"),
                  command=self.handle_login).pack(fill=tk.X, padx=40, pady=30, ipady=10)

        self.root.bind('<Return>', lambda event: self.handle_login())
        self.entry_user.focus_set()

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin")
            return

        # Gọi Controller
        user, msg = self.controller.login(username, password)

        if user:
            # --- TRƯỜNG HỢP THÀNH CÔNG ---
            # 1. Hủy bind phím Enter để tránh lỗi ở màn hình sau
            try:
                self.root.unbind('<Return>')
            except:
                pass  # Bỏ qua nếu không tìm thấy root

            # 2. Xóa giao diện đăng nhập (nếu cần thiết, tùy cách bạn quản lý view)
            # self.destroy() hoặc self.login_frame.destroy() tùy vào cấu trúc class của bạn

            # 3. Chuyển sang màn hình chính
            self.on_success(user)

        else:
            # --- TRƯỜNG HỢP THẤT BẠI ---
            # Hiện đúng cái msg mà Service trả về (Sai pass, Khóa, Không tồn tại...)
            messagebox.showerror("Đăng nhập thất bại", msg)