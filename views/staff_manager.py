import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from views.date_picker_popup import DatePickerPopup  # <--- Import file lịch

class StaffManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.render()

    def render(self):
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))
        
        # Search
        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        tk.Entry(search_frame, width=40, font=("Arial", 11)).pack(side=tk.LEFT, ipady=3)
        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # Button Add
        tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white", 
                  font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat",
                  command=lambda: self.open_dialog(mode="add")).pack(side=tk.RIGHT)

        # --- Table ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "gender", "dob", "phone", "email", "role", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        headers = ["ID", "Họ tên", "Giới tính", "Ngày sinh", "Số điện thoại", "Email", "Chức vụ", ""]
        widths = [50, 150, 60, 80, 100, 180, 80, 80]
        
        for col, header, w in zip(columns, headers, widths):
            self.tree.heading(col, text=header, anchor="w" if col != "actions" else "center")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.action_icons = "✏  🗑"
        
        # Dữ liệu mẫu
        data = [
            ("NV01", "Lê Đức Quý", "Nam", "23/04/2003", "0328666586", "quyle0051@gmail.com", "Nhân viên"),
            ("NV02", "Nguyễn Văn A", "Nam", "01/01/2000", "0909123456", "nguyenvana@gmail.com", "Quản lý"),
        ]
        for item in data:
            display_values = item + (self.action_icons,)
            self.tree.insert("", tk.END, values=display_values)

        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)
        if column == '#8': 
            item_id = self.tree.identify_row(event.y)
            bbox = self.tree.bbox(item_id, column)
            if bbox:
                relative_x = event.x - bbox[0]
                if relative_x < bbox[2] / 2:
                    current_values = self.tree.item(item_id, "values")
                    self.open_dialog(mode="edit", data=current_values)
                else:
                    messagebox.askyesno("Confirm", "Xóa nhân viên?")

    # ---------------------------------------------------------
    # DIALOG THÊM / SỬA NHÂN VIÊN
    # ---------------------------------------------------------
    def open_dialog(self, mode="add", data=None):
        dialog = tk.Toplevel(self.parent)
        title = "THÊM NHÂN VIÊN" if mode == "add" else "SỬA THÔNG TIN NHÂN VIÊN"
        dialog.title(title)
        dialog.geometry("600x650")
        dialog.config(bg="white")
        dialog.grab_set()

        tk.Label(dialog, text=title, font=("Arial", 14, "bold"), bg="white", fg="#333").pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg="white", padx=40)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Helper tạo dòng input (Đã nâng cấp để hỗ trợ Date)
        def create_row(label_text, value="", input_type="entry", options=None):
            row = tk.Frame(form_frame, bg="white", pady=10)
            row.pack(fill=tk.X)
            
            tk.Label(row, text=label_text, font=("Arial", 11), bg="white", fg="#555", width=15, anchor="w").pack(side=tk.LEFT)
            
            inp = None
            if input_type == "combobox":
                inp = ttk.Combobox(row, values=options, font=("Arial", 11), state="readonly")
                inp.set(value)
                inp.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif input_type == "date":
                # Entry chứa ngày
                inp = tk.Entry(row, font=("Arial", 11), bd=0, highlightthickness=1, highlightbackground="#ccc")
                inp.insert(0, value)
                inp.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
                
                # Icon lịch
                lbl_icon = tk.Label(row, text="📅", bg="white", cursor="hand2", font=("Arial", 12))
                lbl_icon.pack(side=tk.LEFT, padx=(5, 0))
                
                # Hàm mở lịch
                def open_cal(e):
                    # Gọi DatePickerPopup và truyền hàm lambda để cập nhật entry
                    DatePickerPopup(dialog, inp.get(), lambda new_date: (inp.delete(0, tk.END), inp.insert(0, new_date)))

                # Bind sự kiện click vào Entry và Icon
                inp.bind("<Button-1>", open_cal)
                lbl_icon.bind("<Button-1>", open_cal)
            else:
                inp = tk.Entry(row, font=("Arial", 11), bd=0, highlightthickness=1, highlightbackground="#ccc")
                inp.insert(0, value)
                inp.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            return inp

        val_name = data[1] if data else ""
        val_gender = data[2] if data else "Nam"
        val_dob = data[3] if data else ""
        val_phone = data[4] if data else ""
        val_email = data[5] if data else ""
        val_role = data[6] if data else "Nhân viên"
        
        create_row("Họ và tên", val_name)
        create_row("Giới tính", val_gender, "combobox", ["Nam", "Nữ", "Khác"])
        
        # --- Sử dụng input_type="date" ---
        create_row("Ngày sinh", val_dob, "date") 
        
        create_row("Số điện thoại", val_phone)
        create_row("Email", val_email)
        create_row("Chức vụ", val_role, "combobox", ["Quản lý", "Nhân viên", "Bán thời gian"])
        
        # --- Sử dụng input_type="date" ---
        create_row("Ngày bắt đầu", "13/11/2021", "date")
        
        create_row("Tài khoản", "admin" if mode=="edit" else "")

        if mode == "edit":
            tk.Label(form_frame, text="Đổi mật khẩu", font=("Arial", 10, "underline"), 
                     bg="white", fg="#1976d2", cursor="hand2").pack(anchor="w", pady=(5, 20), padx=135)

        btn_frame = tk.Frame(dialog, bg="white", pady=20)
        btn_frame.pack(fill=tk.X, padx=40, side=tk.BOTTOM)

        tk.Button(btn_frame, text="Hủy", bg="#ff5722", fg="white", font=("Arial", 10, "bold"), 
                  width=10, relief="flat", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), 
                  width=10, relief="flat", command=dialog.destroy).pack(side=tk.RIGHT)