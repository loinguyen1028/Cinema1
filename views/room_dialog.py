import tkinter as tk
from tkinter import messagebox


class RoomDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", room_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.room_id = room_id
        self.on_success = on_success

        self.title("Thêm phòng chiếu" if mode == "add" else "Cập nhật phòng chiếu")
        self.geometry("420x330")
        self.config(bg="#f5f6f8")
        self.resizable(False, False)
        self.grab_set()

        self.render_ui()

        if mode == "edit" and room_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text=self.title(),
            font=("Arial", 14, "bold"),
            bg="#f5f6f8",
            fg="#333"
        ).pack(anchor="w", pady=(0, 20))

        # ===== TÊN PHÒNG =====
        tk.Label(container, text="Tên phòng chiếu", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_name = tk.Entry(container, font=("Arial", 11))
        self.e_name.pack(fill=tk.X, ipady=4, pady=(0, 12))

        # ===== SỐ HÀNG =====
        tk.Label(container, text="Số hàng ghế (A-Z)", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_rows = tk.Entry(container, font=("Arial", 11))
        self.e_rows.pack(fill=tk.X, ipady=4, pady=(0, 12))

        # ===== SỐ GHẾ MỖI HÀNG =====
        tk.Label(container, text="Số ghế mỗi hàng", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_seats_per_row = tk.Entry(container, font=("Arial", 11))
        self.e_seats_per_row.pack(fill=tk.X, ipady=4, pady=(0, 20))

        # ===== NÚT LƯU =====
        tk.Button(
            container,
            text="Lưu",
            bg="#1976d2",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            command=self.save_action
        ).pack()

        # Nếu là EDIT → không cho sửa cấu trúc ghế
        if self.mode == "edit":
            self.e_rows.config(state="disabled")
            self.e_seats_per_row.config(state="disabled")

    def load_data(self):
        room = self.controller.get_room_by_id(self.room_id)
        if room:
            self.e_name.insert(0, room.room_name)

            # Tính ngược rows & seats_per_row để hiển thị (tham khảo)
            # Không dùng để update
            # Giả sử layout cũ: 10 hàng
            self.e_rows.insert(0, "10")
            self.e_seats_per_row.insert(0, str(room.capacity // 10))

    def save_action(self):
        name = self.e_name.get().strip()
        rows = self.e_rows.get().strip()
        seats_per_row = self.e_seats_per_row.get().strip()

        success, msg = self.controller.save_room(
            self.mode,
            self.room_id,
            name,
            rows,
            seats_per_row
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)
