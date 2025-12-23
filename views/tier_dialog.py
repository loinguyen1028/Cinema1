import tkinter as tk
from tkinter import messagebox


class TierDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", tier_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.tier_id = tier_id
        self.on_success = on_success

        self.title("Thêm hạng mới" if mode == "add" else "Cập nhật hạng")
        self.geometry("400x350")
        self.config(bg="#f5f6f8")
        self.grab_set()  # Chặn tương tác cửa sổ cha

        self.render_ui()

        if mode == "edit" and tier_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=self.title(), font=("Arial", 14, "bold"), bg="#f5f6f8").pack(pady=(0, 20))

        # Tên hạng
        self.e_name = self.create_input(container, "Tên hạng (Ví dụ: Vàng)")
        # Điểm tối thiểu
        self.e_point = self.create_input(container, "Điểm tối thiểu (Ví dụ: 1000)")
        # Giảm giá
        self.e_discount = self.create_input(container, "% Giảm giá (Ví dụ: 5.5)")

        # Button Save
        tk.Button(container, text="Lưu thông tin", bg="#1976d2", fg="white",
                  font=("Arial", 10, "bold"), width=15, command=self.save_action).pack(pady=20)

    def create_input(self, parent, label):
        tk.Label(parent, text=label, bg="#f5f6f8", fg="#555").pack(anchor="w")
        e = tk.Entry(parent, font=("Arial", 11))
        e.pack(fill=tk.X, ipady=4, pady=(0, 10))
        return e

    def load_data(self):
        tier = self.controller.get_detail(self.tier_id)
        if tier:
            self.e_name.insert(0, tier.tier_name)
            self.e_point.insert(0, str(tier.min_point))
            self.e_discount.insert(0, str(tier.discount_percent))

    def save_action(self):
        name = self.e_name.get()
        point = self.e_point.get()
        discount = self.e_discount.get()

        success, msg = self.controller.save(self.mode, self.tier_id, name, point, discount)
        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Lỗi", msg)