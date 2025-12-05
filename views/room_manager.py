import tkinter as tk
from tkinter import ttk, messagebox
from controllers.room_controller import RoomController  # Controller xử lý logic
from views.room_dialog import RoomDialog  # Dialog để thêm/sửa phòng

class RoomManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = RoomController()  # Controller quản lý rạp chiếu

        self.render()

    def render(self):
        container = tk.Frame(self.parent, bg="#f0f2f5")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Bảng dữ liệu (Danh sách phòng chiếu) ---
        table_frame = tk.Frame(container, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("room_id", "room_name", "capacity", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["ID", "Tên phòng", "Sức chứa", "Thao tác"]
        widths = [40, 200, 100, 150]

        for col, header, w in zip(columns, headers, widths):
            self.tree.heading(col, text=header, anchor="w")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.heading("actions", anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Nút Thêm phòng
        add_button = tk.Button(container, text="Thêm Phòng Chiếu", bg="#5c6bc0", fg="white", font=("Arial", 10, "bold"),
                               command=self.open_add_dialog)
        add_button.pack(side=tk.BOTTOM, pady=15)

        # Tải danh sách phòng chiếu
        self.load_rooms()

    def load_rooms(self):
        # Lấy danh sách phòng chiếu từ controller
        rooms = self.controller.get_all_rooms()
        self.update_table(rooms)

    def update_table(self, rooms):
        # Xóa tất cả dữ liệu trong bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_btns = "✏       🗑"  # Sửa và Xóa
        for room in rooms:
            vals = (room.room_id, room.room_name, room.capacity, action_btns)
            self.tree.insert("", tk.END, iid=room.room_id, values=vals)

        # Gắn sự kiện cho cột "Thao tác"
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

    def open_add_dialog(self):
        # Mở hộp thoại thêm phòng chiếu
        RoomDialog(self.parent, self.controller, mode="add", on_success=self.load_rooms)

    def open_edit_dialog(self, room_id):
        # Mở hộp thoại sửa phòng chiếu
        RoomDialog(self.parent, self.controller, mode="edit", room_id=room_id, on_success=self.load_rooms)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column == '#4':  # Cột "Thao tác"
            item_id = self.tree.identify_row(event.y)
            bbox = self.tree.bbox(item_id, column)
            if bbox:
                # Chia cột "Thao tác" thành 2 phần: Sửa và Xóa
                cell_x, _, cell_width, _ = bbox
                rel_x = event.x - cell_x
                w = cell_width / 2

                if rel_x < w:  # Sửa phòng
                    self.open_edit_dialog(item_id)
                else:  # Xóa phòng
                    if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa phòng này?"):
                        success, msg = self.controller.delete_room(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_rooms()
                        else:
                            messagebox.showerror("Lỗi", msg)
