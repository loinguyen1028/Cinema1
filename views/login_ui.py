import tkinter as tk
from tkinter import messagebox
from dao.auth_dao import AuthDAO  # <--- Import file DAO

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_success = on_login_success
        
        # --- QUAN TRỌNG: Khởi tạo DAO tại đây ---
        self.auth_dao = AuthDAO() 
        
        self.root.title("Đăng nhập - LHQ Cinema")
        self.root.geometry("900x600")
        self.root.config(bg="#0f1746")

        # Gọi hàm vẽ giao diện
        self.render_ui()

    def render_ui(self):
        # Container chính
        self.login_frame = tk.Frame(self.root, bg="white", width=400, height=500)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)

        # Tiêu đề
        tk.Label(self.login_frame, text="ĐĂNG NHẬP", font=("Arial", 22, "bold"), bg="white", fg="#0f1746").pack(pady=(50, 10))
        tk.Label(self.login_frame, text="Hệ thống quản lý rạp chiếu phim", font=("Arial", 10), bg="white", fg="#666").pack(pady=(0, 30))

        # Username
        tk.Label(self.login_frame, text="Tài khoản", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.entry_user = tk.Entry(self.login_frame, font=("Arial", 12), bd=1, relief="solid")
        self.entry_user.pack(fill=tk.X, padx=40, pady=5, ipady=5)

        # Password
        tk.Label(self.login_frame, text="Mật khẩu", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=40, pady=(10,0))
        self.entry_pass = tk.Entry(self.login_frame, font=("Arial", 12), bd=1, relief="solid", show="*")
        self.entry_pass.pack(fill=tk.X, padx=40, pady=5, ipady=5)

        # Button Login
        tk.Button(self.login_frame, text="ĐĂNG NHẬP", bg="#ff9800", fg="white", font=("Arial", 11, "bold"),
                  command=self.handle_login).pack(fill=tk.X, padx=40, pady=30, ipady=10)
        
        # Bind phím Enter
        self.root.bind('<Return>', lambda event: self.handle_login())
        self.entry_user.focus_set()

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # --- GỌI DAO ĐỂ XỬ LÝ ---
        # Lỗi cũ của bạn nằm ở đây do thiếu self.auth_dao
        user = self.auth_dao.login(username, password)

        if user:
            # Lấy role từ user trả về
            # Lưu ý: user.role là object, nên cần gọi .role_name
            try:
                role_name = user.role.role_name.lower()
            except AttributeError:
                messagebox.showerror("Lỗi dữ liệu", "User này chưa được gán quyền hạn (Role)!")
                return

            self.login_frame.destroy()
            
            # Chuyển hướng dựa trên role
            if "admin" in role_name:
                self.on_success("admin")
            elif "staff" in role_name:
                self.on_success("staff")
            else:
                messagebox.showerror("Lỗi", f"Quyền '{role_name}' chưa được hỗ trợ trên hệ thống này!")
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tài khoản hoặc mật khẩu!")