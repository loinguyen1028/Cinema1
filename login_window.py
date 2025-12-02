# login_window.py
import tkinter as tk
from tkinter import messagebox
from db import get_connection

class LoginWindow:
    def __init__(self, root, on_login_success):
        """
        on_login_success(user_id, full_name, role_name)
        """
        self.root = root
        self.on_login_success = on_login_success

        self.root.title("Đăng nhập hệ thống rạp chiếu phim")
        self.root.geometry("400x250")

        tk.Label(root, text="Username:").pack(pady=5)
        self.entry_user = tk.Entry(root)
        self.entry_user.pack(pady=5)

        tk.Label(root, text="Password:").pack(pady=5)
        self.entry_pass = tk.Entry(root, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(root, text="Đăng nhập",
                  command=self.login).pack(pady=15)

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Lỗi",
                                   "Vui lòng nhập đầy đủ username và password")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.user_id, u.full_name, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.username = %s AND u.password = %s
            """, (username, password))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        if row:
            user_id, full_name, role_name = row
            messagebox.showinfo("Thành công",
                                f"Xin chào {full_name} ({role_name})")
            self.on_login_success(user_id, full_name, role_name)
        else:
            messagebox.showerror("Sai thông tin",
                                 "Username hoặc password không đúng")
