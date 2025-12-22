import tkinter as tk
# Import hàm in vừa tạo ở Bước 1
# Lưu ý: Sửa đường dẫn import tùy vào cấu trúc thư mục của bạn
from utils.ticket_printer import print_ticket_pdf


class TicketSuccessDialog(tk.Toplevel):
    # Thêm tham số ticket_data vào __init__
    def __init__(self, parent, total_amount, seat_labels="", on_close=None, ticket_data=None):
        super().__init__(parent)
        self.on_close = on_close
        self.ticket_data = ticket_data  # Lưu dữ liệu vé

        self.title("Xuất vé thành công")
        self.geometry("420x400")  # Tăng chiều cao lên xíu để chứa nút In
        self.config(bg="#121212")
        self.resizable(False, False)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() // 2 - 210
        y = parent.winfo_rooty() + parent.winfo_height() // 2 - 200
        self.geometry(f"+{x}+{y}")

        # ===== CARD =====
        card = tk.Frame(self, bg="#1f1f1f", bd=0)
        card.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        # Icon, Title, Subtitle, Divider, Seat info, Total... (GIỮ NGUYÊN CODE CŨ)
        tk.Label(card, text="🎟", font=("Arial", 48), bg="#1f1f1f", fg="#f5c518").pack(pady=(15, 5))
        tk.Label(card, text="XUẤT VÉ THÀNH CÔNG", font=("Arial", 16, "bold"), bg="#1f1f1f", fg="#f5c518").pack(
            pady=(5, 10))
        tk.Label(card, text="Giao dịch đã hoàn tất", font=("Arial", 10), bg="#1f1f1f", fg="#aaaaaa").pack()
        tk.Frame(card, bg="#333", height=1).pack(fill=tk.X, padx=30, pady=15)

        if seat_labels:
            tk.Label(card, text=f"Ghế: {seat_labels}", font=("Arial", 10), bg="#1f1f1f", fg="white").pack(pady=3)

        tk.Label(card, text=f"TỔNG THANH TOÁN", font=("Arial", 10, "bold"), bg="#1f1f1f", fg="#aaaaaa").pack(
            pady=(10, 2))
        tk.Label(card, text=f"{int(total_amount):,} VND", font=("Arial", 20, "bold"), bg="#1f1f1f", fg="#e53935").pack(
            pady=(0, 15))

        # ===== BUTTONS =====
        btn_frame = tk.Frame(card, bg="#1f1f1f")
        btn_frame.pack(pady=15)

        # Nút In Vé (Mới)
        tk.Button(
            btn_frame,
            text="🖨 IN VÉ",
            font=("Arial", 11, "bold"),
            bg="#fff", fg="#333",
            relief="flat", width=12, height=2,
            command=self.handle_print
        ).pack(side=tk.LEFT, padx=5)

        # Nút Hoàn tất
        tk.Button(
            btn_frame,
            text="HOÀN TẤT",
            font=("Arial", 11, "bold"),
            bg="#f5c518", fg="black",
            relief="flat", width=12, height=2,
            command=self.close
        ).pack(side=tk.LEFT, padx=5)

    def handle_print(self):
        if self.ticket_data:
            # Gọi hàm in từ utils
            print_ticket_pdf(self.ticket_data)
        else:
            print("Không có dữ liệu vé để in")

    def close(self):
        if self.on_close:
            self.on_close()
        self.destroy()