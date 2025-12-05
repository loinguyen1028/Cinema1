import tkinter as tk
from tkinter import messagebox

class RoomDialog:
    def __init__(self, parent, controller, mode="add", room_id=None, on_success=None):
        self.parent = parent
        self.controller = controller
        self.mode = mode  # "add" for add, "edit" for edit
        self.room_id = room_id  # Room ID if editing an existing room
        self.on_success = on_success  # Callback function to refresh the room list after success

        self.render()

    def render(self):
        # Create the dialog window (Toplevel)
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Thêm Phòng Chiếu" if self.mode == "add" else "Sửa Phòng Chiếu")

        # Label and Entry for Room Name
        tk.Label(self.dialog, text="Tên Phòng:").grid(row=0, column=0)
        self.entry_name = tk.Entry(self.dialog)
        self.entry_name.grid(row=0, column=1)

        # Label and Entry for Room Capacity
        tk.Label(self.dialog, text="Sức Chứa:").grid(row=1, column=0)
        self.entry_capacity = tk.Entry(self.dialog)
        self.entry_capacity.grid(row=1, column=1)

        # If editing, populate fields with current room data
        if self.mode == "edit":
            room = self.controller.get_room_by_id(self.room_id)
            if room:
                self.entry_name.insert(0, room.room_name)
                self.entry_capacity.insert(0, room.capacity)

        # Save Button
        tk.Button(self.dialog, text="Lưu", command=self.save).grid(row=2, column=0, columnspan=2)

    def save(self):
        room_name = self.entry_name.get()
        capacity = self.entry_capacity.get()

        # Validate inputs
        if not room_name or not capacity:
            messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin phòng!")
            return

        # Convert capacity to integer
        try:
            capacity = int(capacity)
        except ValueError:
            messagebox.showwarning("Thông báo", "Sức chứa phải là một số hợp lệ!")
            return

        # Add or Edit Room based on mode
        if self.mode == "add":
            success, msg = self.controller.add_room(room_name, capacity)
        else:
            success, msg = self.controller.update_room(self.room_id, room_name, capacity)

        if success:
            messagebox.showinfo("Thông báo", msg)
            if self.on_success:
                self.on_success()  # Refresh the room list
            self.dialog.destroy()
        else:
            messagebox.showerror("Lỗi", msg)
