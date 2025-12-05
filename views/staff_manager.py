import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from controllers.staff_controller import StaffController
from views.staff_dialog import StaffDialog


class StaffManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = StaffController()  # Khởi tạo Controller
        self.render()

    def render(self):
        # --- Container chính ---
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        # Search Frame
        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)

        self.entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search)  # Tìm kiếm ngay khi gõ phím

        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # Button Add
        btn_add = tk.Button(toolbar, text="Thêm nhân viên", bg="#5c6bc0", fg="white",
                            font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat", cursor="hand2",
                            command=lambda: self.open_dialog("add"))
        btn_add.pack(side=tk.RIGHT)

        # --- Table Frame ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Cấu hình các cột
        columns = ("id", "name", "gender", "dob", "phone", "email", "role", "start_date", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Cấu hình Header và Width
        headers = ["ID", "Họ tên", "Giới tính", "Ngày sinh", "SĐT", "Email", "Chức vụ", "Ngày vào làm", "Thao tác"]
        widths = [40, 150, 60, 90, 100, 180, 80, 100, 80]

        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h, anchor="w" if col != "actions" else "center")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind sự kiện click vào bảng (để xử lý nút Sửa/Xóa)
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

        # Load dữ liệu lần đầu
        self.load_data()


    # HÀM XỬ LÝ DỮ LIỆU
    def load_data(self):
        """Lấy tất cả nhân viên từ Controller"""
        staff_list = self.controller.get_all()
        self.update_table(staff_list)

    def on_search(self, event):
        """Tìm kiếm khi gõ phím"""
        keyword = self.entry_search.get().strip()
        if keyword:
            staff_list = self.controller.search(keyword)
        else:
            staff_list = self.controller.get_all()
        self.update_table(staff_list)

    def update_table(self, staff_list):
        """Xóa bảng cũ và điền dữ liệu mới"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        action_icons = "✏  🗑"

        for s in staff_list:
            # Lấy thông tin phụ từ cột JSON extra_info
            extra = s.extra_info if s.extra_info else {}

            gender = extra.get("gender", "")
            dob = extra.get("dob", "")
            phone = extra.get("phone", "")
            email = extra.get("email", "")
            start_date = extra.get("start_date", "")

            # Lấy trực tiếp từ quan hệ bảng Role
            role_name = s.role.role_name if s.role else "N/A"

            vals = (s.user_id, s.full_name, gender, dob, phone, email, role_name, start_date, action_icons)

            # Insert vào Treeview, dùng user_id làm iid để dễ truy xuất
            self.tree.insert("", tk.END, iid=s.user_id, values=vals)


    # XỬ LÝ SỰ KIỆN CLICK (SỬA / XÓA)
    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return

        column = self.tree.identify_column(event.x)

        # Cột actions là cột thứ 9 (#9)
        if column == '#9':
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            bbox = self.tree.bbox(item_id, column)
            if bbox:
                cell_x, _, cell_width, _ = bbox
                rel_x = event.x - cell_x

                # Logic chia đôi ô: [ Sửa ] | [ Xóa ]
                if rel_x < cell_width / 2:
                    # --- NÚT SỬA ---
                    self.open_dialog("edit", item_id)
                else:
                    # --- NÚT XÓA ---
                    # Lấy tên nhân viên từ cột thứ 2 (index 1) để hỏi xác nhận
                    name = self.tree.item(item_id, "values")[1]

                    if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa nhân viên: {name}?"):
                        success, msg = self.controller.delete(item_id)
                        if success:
                            messagebox.showinfo("Thành công", msg)
                            self.load_data()  # Refresh lại bảng
                        else:
                            messagebox.showerror("Lỗi", msg)

    #Mở dialog thêm sửa
    def open_dialog(self, mode, staff_id=None):
        # Gọi StaffDialog và truyền hàm load_data để tự động refresh sau khi lưu
        StaffDialog(self.parent, self.controller, mode, staff_id, on_success=self.load_data)