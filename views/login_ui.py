import tkinter as tk
from tkinter import messagebox
from dao.auth_dao import AuthDAO


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_success = on_login_success  # Hàm callback (launch_app bên main.py)

        # Khởi tạo DAO
        self.auth_dao = AuthDAO()

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
            messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Gọi DAO kiểm tra đăng nhập
        user = self.auth_dao.login(username, password)

        if user:
            # Đăng nhập thành công
            self.login_frame.destroy()

            # QUAN TRỌNG: Truyền nguyên object user qua main.py
            # Để main.py tự xử lý việc lấy role và user_id
            self.on_success(user)
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tài khoản hoặc mật khẩu!")