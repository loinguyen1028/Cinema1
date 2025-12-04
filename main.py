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

def launch_app(role):
    """Hàm khởi tạo giao diện chính dựa trên quyền"""
    # Xóa giao diện Login
    for widget in root.winfo_children():
        widget.destroy()

    # Định nghĩa hàm logout để truyền vào bên trong các App
    def logout_handler():
        # Khi App gọi hàm này -> Quay lại màn hình Login
        root.after(50, show_login)

    # Khởi tạo App và truyền hàm logout_handler vào
    if role == "admin":
        CinemaApp(root, on_logout=logout_handler) 
    elif role == "staff":
        StaffApp(root, on_logout=logout_handler)

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("LHQ Cinema System")
    
    # Bắt đầu bằng màn hình Login
    show_login()
    
    root.mainloop()