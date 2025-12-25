import tkinter as tk
from tkinter import messagebox


class PaymentConfirmDialog(tk.Toplevel):
    def __init__(self, parent, total_amount, on_confirm):
        super().__init__(parent)
        self.total_amount = total_amount
        self.on_confirm = on_confirm
        self.result = False

        self.colors = {
            "bg": "#0f172a",
            "card": "#1f2933",
            "panel": "#111827",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444",
            "success": "#22c55e"
        }

        self.title("Xác nhận thanh toán")
        self.geometry("420x380")
        self.config(bg=self.colors["bg"])
        self.grab_set()

        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 190
        self.geometry(f"+{x}+{y}")

        self.render_ui()
        self.e_received.focus_set()

    def render_ui(self):
        card = tk.Frame(self, bg=self.colors["card"], padx=25, pady=25)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            card,
            text="TỔNG THANH TOÁN",
            font=("Arial", 10),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack()

        tk.Label(
            card,
            text=f"{int(self.total_amount):,} đ",
            font=("Arial", 22, "bold"),
            bg=self.colors["card"],
            fg=self.colors["danger"]
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="Tiền khách đưa",
            font=("Arial", 11, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w")

        self.e_received = tk.Entry(
            card,
            font=("Arial", 15),
            justify="right",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat"
        )
        self.e_received.pack(fill=tk.X, ipady=8, pady=(6, 0))
        self.e_received.bind("<KeyRelease>", self.calculate_change)

        tk.Label(
            card,
            text="(Nhập số tiền khách đưa)",
            font=("Arial", 9, "italic"),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="e", pady=(2, 0))

        tk.Label(
            card,
            text="Tiền thừa trả khách",
            font=("Arial", 11, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w", pady=(22, 6))

        self.lbl_change = tk.Label(
            card,
            text="0 đ",
            font=("Arial", 16, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["success"],
            pady=10
        )
        self.lbl_change.pack(fill=tk.X)

        btn_frame = tk.Frame(card, bg=self.colors["card"])
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(25, 0))

        btn_cancel = tk.Button(
            btn_frame,
            text="HỦY",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.destroy
        )
        btn_cancel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        self.btn_confirm = tk.Button(
            btn_frame,
            text="HOÀN TẤT THANH TOÁN",
            bg="#374151",
            fg="#9ca3af",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=12,
            state="disabled",
            command=self.confirm_action
        )
        self.btn_confirm.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.bind("<Return>", lambda e: self.confirm_action())

    def calculate_change(self, event=None):
        raw_val = self.e_received.get().replace(",", "").replace(".", "").strip()

        if not raw_val:
            self.lbl_change.config(text="0 đ", fg=self.colors["success"])
            self.btn_confirm.config(state="disabled", bg="#374151", fg="#aaa")
            return

        if not raw_val.isdigit():
            return

        received = int(raw_val)
        change = received - self.total_amount

        if change >= 0:
            self.lbl_change.config(
                text=f"{int(change):,} đ",
                fg=self.colors["success"]
            )
            self.btn_confirm.config(
                state="normal",
                bg=self.colors["primary"],
                fg="#000"
            )
        else:
            self.lbl_change.config(
                text="Thiếu tiền!",
                fg=self.colors["danger"]
            )
            self.btn_confirm.config(
                state="disabled",
                bg="#374151",
                fg="#aaa"
            )

    def confirm_action(self):
        if self.btn_confirm['state'] == 'normal':
            self.result = True
            if self.on_confirm:
                self.on_confirm()
            self.destroy()
