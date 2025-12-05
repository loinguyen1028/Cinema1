import tkinter as tk
from views.Cinema_ui import CinemaApp
from views.staff_ui import StaffApp
from views.login_ui import LoginWindow


def show_login():
    """Hàm hiển thị màn hình đăng nhập"""
    # Xóa sạch các widget hiện tại trên root
    for widget in root.winfo_children():
        widget.destroy()

    # Hiện Login, khi đăng nhập thành công thì gọi launch_app
    LoginWindow(root, on_login_success=launch_app)


# --- SỬA LỖI Ở ĐÂY ---
def launch_app(user):  # 1. Đổi tên tham số từ 'role' thành 'user' cho khớp logic
    for widget in root.winfo_children():
        widget.destroy()

    def logout_handler():
        root.after(50, show_login)

    # Lấy tên Role từ object User
    try:
        # Lấy tên role và chuyển về chữ thường (vd: "admin", "staff")
        role_name = user.role.role_name.lower()
        user_id = user.user_id
    except AttributeError:
        role_name = ""
        user_id = None
        print("Lỗi: Không lấy được thông tin Role của user")

    # 2. So sánh với chữ thường ("admin", "staff") vì đã .lower() ở trên
    if "admin" in role_name:
        CinemaApp(root, user_id=user_id, on_logout=logout_handler)
    elif "staff" in role_name:
        StaffApp(root, user_id=user_id, on_logout=logout_handler)
    else:
        # Trường hợp không khớp quyền nào
        tk.Label(root, text=f"Lỗi: Quyền '{role_name}' chưa được phân quyền truy cập!", font=("Arial", 14)).pack(
            pady=50)
        tk.Button(root, text="Quay lại Đăng nhập", command=logout_handler).pack()


# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("LHQ Cinema System")

    # Bắt đầu bằng màn hình Login
    show_login()

    root.mainloop()