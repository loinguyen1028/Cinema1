import tkinter as tk
from tkinter import ttk, messagebox


class RoomDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", room_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.room_id = room_id
        self.on_success = on_success

        self.title("Thêm phòng chiếu" if mode == "add" else "Cập nhật phòng chiếu")
        self.geometry("400x300")
        self.config(bg="#f5f6f8")
        self.grab_set()

        self.render_ui()

        # Load dữ liệu nếu là chế độ Sửa
        if mode == "edit" and room_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=self.title(), font=("Arial", 14, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # 1. Tên phòng
        tk.Label(container, text="Tên phòng chiếu", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_name = tk.Entry(container, font=("Arial", 11))
        self.e_name.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 2. Số lượng ghế
        tk.Label(container, text="Tổng số ghế (Capacity)", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_seats = tk.Entry(container, font=("Arial", 11))
        self.e_seats.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # Nút Lưu
        tk.Button(container, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                  width=15, command=self.save_action).pack(pady=20)

    def load_data(self):
        # Gọi controller để lấy thông tin phòng
        room = self.controller.get_room_by_id(self.room_id)
        if room:
            self.e_name.insert(0, room.room_name)
            self.e_seats.insert(0, str(room.capacity))

    def save_action(self):
        name = self.e_name.get().strip()
        seats = self.e_seats.get().strip()

        # --- SỬA LỖI TẠI ĐÂY: Gọi hàm save_room thay vì update_room ---
        success, msg = self.controller.save_room(self.mode, self.room_id, name, seats)

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)