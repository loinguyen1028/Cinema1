import tkinter as tk


class TicketSuccessDialog(tk.Toplevel):
    def __init__(self, parent, total_amount, seat_labels="", on_close=None):
        super().__init__(parent)
        self.on_close = on_close

        self.title("Xuất vé thành công")
        self.geometry("420x320")
        self.config(bg="#121212")
        self.resizable(False, False)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() // 2 - 210
        y = parent.winfo_rooty() + parent.winfo_height() // 2 - 160
        self.geometry(f"+{x}+{y}")

        # ===== CARD =====
        card = tk.Frame(self, bg="#1f1f1f", bd=0)
        card.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        # Icon
        tk.Label(
            card,
            text="🎟",
            font=("Arial", 48),
            bg="#1f1f1f",
            fg="#f5c518"
        ).pack(pady=(15, 5))

        # Title
        tk.Label(
            card,
            text="XUẤT VÉ THÀNH CÔNG",
            font=("Arial", 16, "bold"),
            bg="#1f1f1f",
            fg="#f5c518"
        ).pack(pady=(5, 10))

        # Subtitle
        tk.Label(
            card,
            text="Giao dịch đã hoàn tất",
            font=("Arial", 10),
            bg="#1f1f1f",
            fg="#aaaaaa"
        ).pack()

        # Divider
        tk.Frame(card, bg="#333", height=1).pack(fill=tk.X, padx=30, pady=15)

        # Seat info (nếu có)
        if seat_labels:
            tk.Label(
                card,
                text=f"Ghế: {seat_labels}",
                font=("Arial", 10),
                bg="#1f1f1f",
                fg="white"
            ).pack(pady=3)

        # Total
        tk.Label(
            card,
            text=f"TỔNG THANH TOÁN",
            font=("Arial", 10, "bold"),
            bg="#1f1f1f",
            fg="#aaaaaa"
        ).pack(pady=(10, 2))

        tk.Label(
            card,
            text=f"{int(total_amount):,} VND",
            font=("Arial", 20, "bold"),
            bg="#1f1f1f",
            fg="#e53935"
        ).pack(pady=(0, 15))

        # Button
        tk.Button(
            card,
            text="HOÀN TẤT",
            font=("Arial", 11, "bold"),
            bg="#f5c518",
            fg="black",
            relief="flat",
            width=18,
            height=2,
            command=self.close
        ).pack(pady=(5, 15))

    def close(self):
        if self.on_close:
            self.on_close()
        self.destroy()
