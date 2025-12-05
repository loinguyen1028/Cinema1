import tkinter as tk
from tkinter import messagebox
from controllers.auth_controller import AuthController


class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, user_id):  # Nhận user_id thay vì controller cũ
        super().__init__(parent)
        self.user_id = user_id
        self.controller = AuthController()

        self.title("Đổi mật khẩu")
        self.geometry("400x320")  # Tăng chiều cao
        self.config(bg="white")
        self.resizable(False, False)
        self.grab_set()

        self.render_ui()

    def render_ui(self):
        container = tk.Frame(self, bg="white", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Đổi mật khẩu", font=("Arial", 16, "bold"), bg="white", fg="#0f1746").pack(anchor="w",
                                                                                                            pady=(0,
                                                                                                                  20))

        # 1. Mật khẩu cũ
        tk.Label(container, text="Mật khẩu cũ", bg="white", fg="#555").pack(anchor="w")
        self.e_old = tk.Entry(container, font=("Arial", 11), show="*")
        self.e_old.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 2. Mật khẩu mới
        tk.Label(container, text="Mật khẩu mới", bg="white", fg="#555").pack(anchor="w")
        self.e_new = tk.Entry(container, font=("Arial", 11), show="*")
        self.e_new.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 3. Nhập lại
        tk.Label(container, text="Nhập lại mật khẩu mới", bg="white", fg="#555").pack(anchor="w")
        self.e_confirm = tk.Entry(container, font=("Arial", 11), show="*")
        self.e_confirm.pack(fill=tk.X, ipady=4, pady=(0, 10))

        btn_frame = tk.Frame(container, bg="white", pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Hủy", bg="#ddd", fg="#333", width=10, relief="flat", command=self.destroy).pack(
            side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Lưu", bg="#ff9800", fg="white", width=10, relief="flat",
                  command=self.save_action).pack(side=tk.RIGHT)

    def save_action(self):
        old = self.e_old.get().strip()
        new = self.e_new.get().strip()
        confirm = self.e_confirm.get().strip()

        success, msg = self.controller.change_password(self.user_id, old, new, confirm)

        if success:
            messagebox.showinfo("Thành công", msg)
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)