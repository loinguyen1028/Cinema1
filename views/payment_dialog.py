import tkinter as tk
from tkinter import messagebox


class PaymentConfirmDialog(tk.Toplevel):
    def __init__(self, parent, total_amount, on_confirm):
        super().__init__(parent)
        self.total_amount = total_amount
        self.on_confirm = on_confirm
        self.result = False  # Trạng thái trả về

        self.title("Xác nhận thanh toán")
        self.geometry("400x350")
        self.config(bg="white")
        self.grab_set()  # Chặn tương tác màn hình dưới

        # Căn giữa màn hình
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 175
        self.geometry(f"+{x}+{y}")

        self.render_ui()

        # Focus vào ô nhập tiền ngay khi mở
        self.e_received.focus_set()

    def render_ui(self):
        container = tk.Frame(self, bg="white", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Tổng tiền cần thanh toán
        tk.Label(container, text="TỔNG THANH TOÁN", font=("Arial", 10), bg="white", fg="#555").pack()
        tk.Label(container, text=f"{int(self.total_amount):,} VND", font=("Arial", 20, "bold"), bg="white",
                 fg="#d32f2f").pack(pady=(0, 20))

        # Tiền khách đưa
        tk.Label(container, text="Tiền khách đưa:", font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        self.e_received = tk.Entry(container, font=("Arial", 14), justify="right", bd=2, relief="solid")
        self.e_received.pack(fill=tk.X, ipady=5, pady=(5, 0))
        self.e_received.bind("<KeyRelease>", self.calculate_change)  # Gõ phím là tính tiền

        # Gợi ý nhanh (Option)
        tk.Label(container, text="(Nhập số tiền khách đưa)", font=("Arial", 9, "italic"), bg="white", fg="#888").pack(
            anchor="e")

        # Tiền thừa trả khách
        tk.Label(container, text="Tiền thừa trả khách:", font=("Arial", 11, "bold"), bg="white").pack(anchor="w",
                                                                                                      pady=(20, 5))
        self.lbl_change = tk.Label(container, text="0 VND", font=("Arial", 16, "bold"), bg="#f1f8e9", fg="#2e7d32",
                                   width=20, pady=5)
        self.lbl_change.pack(fill=tk.X)

        # Nút xác nhận
        btn_frame = tk.Frame(container, bg="white", pady=20)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(btn_frame, text="Hủy bỏ", width=10, bg="#eee", command=self.destroy).pack(side=tk.LEFT)
        self.btn_confirm = tk.Button(btn_frame, text="HOÀN TẤT", width=15, bg="#1976d2", fg="white",
                                     font=("Arial", 10, "bold"),
                                     command=self.confirm_action, state="disabled")  # Mặc định khóa nút
        self.btn_confirm.pack(side=tk.RIGHT)

        # Bind phím Enter để xác nhận nhanh
        self.bind("<Return>", lambda e: self.confirm_action())

    def calculate_change(self, event=None):
        raw_val = self.e_received.get().replace(",", "").replace(".", "").strip()

        if not raw_val:
            self.lbl_change.config(text="0 VND")
            self.btn_confirm.config(state="disabled", bg="#90caf9")
            return

        if not raw_val.isdigit():
            return

        received = int(raw_val)
        change = received - self.total_amount

        # Format lại số tiền khách đưa (thêm dấu phẩy cho dễ nhìn)
        # (Lưu ý: Logic này hơi phức tạp với Entry, có thể bỏ qua nếu muốn đơn giản)

        if change >= 0:
            self.lbl_change.config(text=f"{int(change):,} VND", fg="#2e7d32")
            self.btn_confirm.config(state="normal", bg="#1976d2")
        else:
            self.lbl_change.config(text="Thiếu tiền!", fg="red")
            self.btn_confirm.config(state="disabled", bg="#90caf9")

    def confirm_action(self):
        if self.btn_confirm['state'] == 'normal':
            self.result = True
            if self.on_confirm: self.on_confirm()
            self.destroy()