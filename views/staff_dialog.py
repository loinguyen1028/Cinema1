import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup


class StaffDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", staff_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.staff_id = staff_id
        self.on_success = on_success

        self.title("Thêm nhân viên" if mode == "add" else "Cập nhật nhân viên")
        self.geometry("600x700")  # Tăng chiều cao xíu cho thoáng
        self.config(bg="#f5f6f8")
        self.grab_set()

        # Lấy danh sách Role từ DB để đổ vào Combobox
        self.roles_list = self.controller.get_roles()
        self.role_map = {r.role_name: r.role_id for r in self.roles_list}

        self.render_ui()

        if mode == "edit" and staff_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=40, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=self.title(), font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # 1. Thông tin cá nhân
        self.e_name = self.create_row(container, "Họ và tên")

        tk.Label(container, text="Giới tính", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.cbo_gender = ttk.Combobox(container, values=["Nam", "Nữ", "Khác"], font=("Arial", 11), state="readonly")
        self.cbo_gender.current(0)
        self.cbo_gender.pack(fill=tk.X, ipady=4, pady=(0, 10))

        tk.Label(container, text="Ngày sinh", bg="#f5f6f8", fg="#555").pack(anchor="w")
        f_dob = tk.Frame(container, bg="#f5f6f8")
        f_dob.pack(fill=tk.X, pady=(0, 10))
        self.e_dob = tk.Entry(f_dob, font=("Arial", 11))
        self.e_dob.pack(side=tk.LEFT, ipady=4, fill=tk.X, expand=True)
        self.create_calendar_btn(f_dob, self.e_dob)

        self.e_phone = self.create_row(container, "Số điện thoại")
        self.e_email = self.create_row(container, "Email")

        # 2. Thông tin công việc
        tk.Label(container, text="Ngày bắt đầu làm việc", bg="#f5f6f8", fg="#555").pack(anchor="w")
        f_start = tk.Frame(container, bg="#f5f6f8")
        f_start.pack(fill=tk.X, pady=(0, 10))
        self.e_start_date = tk.Entry(f_start, font=("Arial", 11))
        self.e_start_date.pack(side=tk.LEFT, ipady=4, fill=tk.X, expand=True)
        self.create_calendar_btn(f_start, self.e_start_date)

        # 3. Tài khoản & Quyền hạn
        lbl_acc = tk.LabelFrame(container, text="Thông tin đăng nhập", bg="#f5f6f8", fg="#333",
                                font=("Arial", 10, "bold"), padx=10, pady=10)
        lbl_acc.pack(fill=tk.X, pady=10)

        tk.Label(lbl_acc, text="Tên tài khoản", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_username = tk.Entry(lbl_acc, font=("Arial", 11))
        self.e_username.pack(fill=tk.X, ipady=4, pady=(0, 10))

        tk.Label(lbl_acc, text="Quyền hạn (Role)", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.cbo_role = ttk.Combobox(lbl_acc, values=list(self.role_map.keys()), font=("Arial", 11), state="readonly")
        if self.role_map:
            self.cbo_role.current(0)
        self.cbo_role.pack(fill=tk.X, ipady=4)

        # --- PHẦN NÚT BẤM (ĐÃ SỬA LỖI: THÊM VÀO ĐÂY) ---
        btn_frame = tk.Frame(container, bg="#f5f6f8", pady=20)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Nút Hủy
        tk.Button(btn_frame, text="Hủy", bg="#ff5722", fg="white", font=("Arial", 10, "bold"),
                  width=10, relief="flat", command=self.destroy).pack(side=tk.RIGHT, padx=10)

        # Nút Lưu
        tk.Button(btn_frame, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                  width=10, relief="flat", command=self.save_action).pack(side=tk.RIGHT)

    # --- Helper Functions ---
    def create_row(self, parent, label):
        tk.Label(parent, text=label, bg="#f5f6f8", fg="#555").pack(anchor="w")
        e = tk.Entry(parent, font=("Arial", 11))
        e.pack(fill=tk.X, ipady=4, pady=(0, 10))
        return e

    def create_calendar_btn(self, parent, entry_widget):
        def open_cal(e):
            DatePickerPopup(self, entry_widget.get(),
                            lambda d: (entry_widget.delete(0, tk.END), entry_widget.insert(0, d)),
                            trigger_widget=entry_widget)

        lbl_icon = tk.Label(parent, text="📅", bg="#f5f6f8", cursor="hand2", font=("Arial", 12))
        lbl_icon.pack(side=tk.LEFT, padx=5)
        lbl_icon.bind("<Button-1>", open_cal)
        entry_widget.bind("<Button-1>", open_cal)

    def load_data(self):
        staff = self.controller.get_detail(self.staff_id)
        if staff:
            self.e_name.insert(0, staff.full_name)
            self.e_username.insert(0, staff.username)
            self.e_username.config(state="readonly")

            if staff.role:
                self.cbo_role.set(staff.role.role_name)

            extra = staff.extra_info if staff.extra_info else {}
            self.cbo_gender.set(extra.get("gender", ""))
            self.e_dob.insert(0, extra.get("dob", ""))
            self.e_phone.insert(0, extra.get("phone", ""))
            self.e_email.insert(0, extra.get("email", ""))
            self.e_start_date.insert(0, extra.get("start_date", ""))

    def save_action(self):
        role_name = self.cbo_role.get()
        role_id = self.role_map.get(role_name)

        data = {
            "name": self.e_name.get().strip(),
            "gender": self.cbo_gender.get(),
            "dob": self.e_dob.get(),
            "phone": self.e_phone.get().strip(),
            "email": self.e_email.get().strip(),
            "start_date": self.e_start_date.get(),
            "username": self.e_username.get().strip(),
            "role_id": role_id
        }

        success, msg = self.controller.save(self.mode, self.staff_id, data)

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)