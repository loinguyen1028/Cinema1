import tkinter as tk
from views.Cinema_ui import CinemaApp
from views.staff_ui import StaffApp
from views.login_ui import LoginWindow


def show_login():
    """Hàm hiển thị màn hình đăng nhập"""
    for widget in root.winfo_children():
        widget.destroy()

    LoginWindow(root, on_login_success=launch_app)


def launch_app(user):
    for widget in root.winfo_children():
        widget.destroy()

    def logout_handler():
        root.after(50, show_login)

    try:
        role_name = user.role.role_name.lower()
        user_id = user.user_id
    except AttributeError:
        role_name = ""
        user_id = None
        print("Lỗi: Không lấy được thông tin Role của user")

    if "admin" in role_name:
        CinemaApp(root, user_id=user_id, on_logout=logout_handler)
    elif "staff" in role_name:
        StaffApp(root, user_id=user_id, on_logout=logout_handler)
    else:
        tk.Label(root, text=f"Lỗi: Quyền '{role_name}' chưa được phân quyền truy cập!", font=("Arial", 14)).pack(
            pady=50)
        tk.Button(root, text="Quay lại Đăng nhập", command=logout_handler).pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("LHQ Cinema System")

    show_login()

    root.mainloop()