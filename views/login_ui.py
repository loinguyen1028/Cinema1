import tkinter as tk
from tkinter import messagebox
from dao.auth_dao import AuthDAO
from controllers.auth_controller import AuthController


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_success = on_login_success

        self.auth_dao = AuthDAO()
        self.controller = AuthController()

        self.root.title("Đăng nhập - LHQ Cinema")
        self.root.geometry("900x600")
        self.root.config(bg="#0f1746")

        self.render_ui()

    def render_ui(self):
        container = tk.Frame(self.root, bg="#0b0b0b")
        container.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(container, bg="#0b0b0b")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            left,
            text="LHQ CINEMA",
            font=("Arial Black", 36),
            fg="#f5c518",
            bg="#0b0b0b"
        ).place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(
            left,
            text="Cinema Management System",
            font=("Arial", 12),
            fg="#b0b0b0",
            bg="#0b0b0b"
        ).place(relx=0.5, rely=0.55, anchor="center")

        right = tk.Frame(container, bg="#111111", width=420)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        tk.Label(
            right,
            text="ĐĂNG NHẬP",
            font=("Arial", 22, "bold"),
            fg="#f5c518",
            bg="#111111"
        ).pack(pady=(70, 10))

        tk.Label(
            right,
            text="Quản lý rạp chiếu phim",
            font=("Arial", 10),
            fg="#b0b0b0",
            bg="#111111"
        ).pack(pady=(0, 40))

        tk.Label(right, text="Tài khoản", fg="#ffffff", bg="#111111").pack(anchor="w", padx=40)
        self.entry_user = tk.Entry(
            right,
            font=("Arial", 12),
            bg="#1c1c1c",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.entry_user.pack(fill=tk.X, padx=40, pady=8, ipady=6)

        tk.Label(right, text="Mật khẩu", fg="#ffffff", bg="#111111").pack(anchor="w", padx=40)
        self.entry_pass = tk.Entry(
            right,
            font=("Arial", 12),
            bg="#1c1c1c",
            fg="white",
            insertbackground="white",
            relief="flat",
            show="*"
        )
        self.entry_pass.pack(fill=tk.X, padx=40, pady=8, ipady=6)

        self.btn_login = tk.Button(
            right,
            text="ĐĂNG NHẬP",
            bg="#f5c518",
            fg="#000000",
            font=("Arial", 11, "bold"),
            relief="flat",
            command=self.handle_login,
            cursor="hand2"
        )
        self.btn_login.pack(fill=tk.X, padx=40, pady=35, ipady=10)

        self.btn_login.bind("<Enter>", lambda e: self.btn_login.config(bg="#ffd54f"))
        self.btn_login.bind("<Leave>", lambda e: self.btn_login.config(bg="#f5c518"))

        self.root.bind("<Return>", lambda e: self.handle_login())
        self.entry_user.focus_set()

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin")
            return

        user, msg = self.controller.login(username, password)

        if user:
            try:
                self.root.unbind('<Return>')
            except:
                pass

            self.on_success(user)
        else:
            messagebox.showerror("Đăng nhập thất bại", msg)
