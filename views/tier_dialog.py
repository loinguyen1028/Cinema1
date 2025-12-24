import tkinter as tk
from tkinter import messagebox


class TierDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", tier_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.tier_id = tier_id
        self.on_success = on_success

        # ===== STAFF THEME =====
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444"
        }

        self.title("Thêm hạng mới" if mode == "add" else "Cập nhật hạng")
        self.geometry("440x460")
        self.config(bg=self.colors["bg"])
        self.resizable(True, True)
        self.grab_set()

        self.render_ui()

        if mode == "edit" and tier_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(
            self,
            bg=self.colors["card"],
            padx=30,
            pady=25
        )
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ===== TITLE =====
        tk.Label(
            container,
            text="THÔNG TIN HẠNG THÀNH VIÊN",
            font=("Arial", 14, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(pady=(0, 20))

        # ===== INPUTS =====
        self.e_name = self.create_input(container, "Tên hạng")
        self.e_point = self.create_input(container, "Điểm tối thiểu")
        self.e_discount = self.create_input(container, "Giảm giá (%)")

        # ===== BUTTONS =====
        btn_frame = tk.Frame(container, bg=self.colors["card"])
        btn_frame.pack(pady=25)

        tk.Button(
            btn_frame,
            text="Hủy",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Arial", 10, "bold"),
            width=12,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Lưu",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 10, "bold"),
            width=12,
            relief="flat",
            cursor="hand2",
            command=self.save_action
        ).pack(side=tk.LEFT, padx=10)

    def create_input(self, parent, label):
        tk.Label(
            parent,
            text=label,
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Arial", 10)
        ).pack(anchor="w")

        e = tk.Entry(
            parent,
            font=("Arial", 11),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            insertbackground=self.colors["primary"],
            relief="flat"
        )
        e.pack(fill=tk.X, ipady=6, pady=(4, 14))
        return e

    # ===== DATA =====
    def load_data(self):
        tier = self.controller.get_detail(self.tier_id)
        if tier:
            self.e_name.insert(0, tier.tier_name)
            self.e_point.insert(0, str(tier.min_point))
            self.e_discount.insert(0, str(tier.discount_percent))

    # ===== SAVE =====
    def save_action(self):
        name = self.e_name.get()
        point = self.e_point.get()
        discount = self.e_discount.get()

        success, msg = self.controller.save(
            self.mode,
            self.tier_id,
            name,
            point,
            discount
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Lỗi", msg)
