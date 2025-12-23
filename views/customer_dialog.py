import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup


class CustomerDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", customer_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.customer_id = customer_id
        self.on_success = on_success

        self.title("Thêm khách hàng" if mode == "add" else "Cập nhật khách hàng")
        self.geometry("500x500")
        self.config(bg="#f5f6f8")
        self.grab_set()

        self.render_ui()

        if mode == "edit" and customer_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=self.title(), font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # Tên
        self.e_name = self.create_input(container, "Họ và tên")
        # SĐT
        self.e_phone = self.create_input(container, "Số điện thoại")
        # Email
        self.e_email = self.create_input(container, "Email")

        # Ngày sinh (Có lịch)
        tk.Label(container, text="Ngày sinh", bg="#f5f6f8", fg="#555").pack(anchor="w")
        f_dob = tk.Frame(container, bg="#f5f6f8")
        f_dob.pack(fill=tk.X, pady=(0, 10))
        self.e_dob = tk.Entry(f_dob, font=("Arial", 11), width=30)
        self.e_dob.pack(side=tk.LEFT, ipady=4, fill=tk.X, expand=True)

        def open_cal(e):
            DatePickerPopup(self, self.e_dob.get(),
                            lambda d: (self.e_dob.delete(0, tk.END), self.e_dob.insert(0, d)),
                            trigger_widget=self.e_dob)

        self.e_dob.bind("<Button-1>", open_cal)
        tk.Label(f_dob, text="📅", bg="#f5f6f8").pack(side=tk.LEFT, padx=5)

        # --- KHU VỰC ĐIỂM & HẠNG ---
        row_level = tk.Frame(container, bg="#f5f6f8")
        row_level.pack(fill=tk.X)

        # 1. Điểm tích lũy
        f_points = tk.Frame(row_level, bg="#f5f6f8")
        f_points.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(f_points, text="Điểm tích lũy", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_points = tk.Entry(f_points, font=("Arial", 11))
        self.e_points.insert(0, "0")
        self.e_points.pack(fill=tk.X, ipady=4)

        # 2. Hạng thành viên
        f_level = tk.Frame(row_level, bg="#f5f6f8")
        f_level.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(f_level, text="Hạng thành viên", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.cbo_level = ttk.Combobox(f_level, values=["Thân thiết", "Bạc", "Vàng", "Kim cương"], font=("Arial", 11),
                                      state="readonly")
        self.cbo_level.current(0)
        self.cbo_level.pack(fill=tk.X, ipady=4)

        # --- XỬ LÝ KHÓA NHẬP LIỆU ---
        # Nếu là thêm mới (add), khóa ô Điểm và Hạng lại
        if self.mode == "add":
            self.e_points.config(state='readonly')  # Chỉ đọc, không cho sửa
            self.cbo_level.config(state='disabled')  # Không cho xổ xuống chọn

        # Nút Lưu
        tk.Button(container, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 11, "bold"),
                  width=15, command=self.save_action).pack(pady=30)

    def create_input(self, parent, label):
        tk.Label(parent, text=label, bg="#f5f6f8", fg="#555").pack(anchor="w")
        e = tk.Entry(parent, font=("Arial", 11))
        e.pack(fill=tk.X, ipady=4, pady=(0, 10))
        return e

    def load_data(self):
        cus = self.controller.get_detail(self.customer_id)
        if cus:
            self.e_name.insert(0, cus.name)
            self.e_phone.insert(0, cus.phone if cus.phone else "")
            self.e_email.insert(0, cus.email if cus.email else "")

            extra = cus.extra_info if cus.extra_info else {}
            self.e_dob.insert(0, extra.get("dob", ""))

            self.e_points.config(state='normal')
            self.e_points.delete(0, tk.END)

            # --- SỬA ĐOẠN NÀY ---
            # Lấy từ cột points
            self.e_points.insert(0, str(cus.points))
            self.e_points.config(state='readonly')

            # Hạng thành viên
            self.cbo_level.config(state='normal')
            # Lấy tên hạng từ relationship
            tier_name = cus.tier.tier_name if cus.tier else "Thân thiết"
            self.cbo_level.set(tier_name)
            self.cbo_level.config(state='disabled')

    def save_action(self):
        name = self.e_name.get().strip()
        phone = self.e_phone.get().strip()
        email = self.e_email.get().strip()
        dob = self.e_dob.get().strip()
        points = self.e_points.get().strip()
        level = self.cbo_level.get()

        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên khách hàng")
            return

        success, msg = self.controller.save(self.mode, self.customer_id, name, phone, email, dob, points, level)

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)