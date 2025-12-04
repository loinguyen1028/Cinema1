import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CustomerManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.render()

    def render(self):
        # --- Container chính ---
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # --- Toolbar (Tìm kiếm & Thêm) ---
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))
        
        # Search Box
        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        tk.Entry(search_frame, width=40, font=("Arial", 11)).pack(side=tk.LEFT, ipady=3)
        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        # Button Add
        btn_add = tk.Button(toolbar, text="Thêm", bg="#5c6bc0", fg="white", 
                            font=("Arial", 10, "bold"), padx=20, pady=5, relief="flat", cursor="hand2")
        btn_add.pack(side=tk.RIGHT)

        # --- Bảng dữ liệu ---
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "phone", "email", "dob", "points", "level", "created_at", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Định nghĩa tiêu đề cột
        headers = ["ID", "Tên khách hàng", "SĐT", "Email", "Ngày sinh", "Điểm", "Hạng", "Ngày tạo", ""]
        widths = [40, 150, 100, 180, 90, 60, 80, 120, 80]
        
        for col, header, w in zip(columns, headers, widths):
            self.tree.heading(col, text=header, anchor="w" if col != "actions" else "center")
            self.tree.column(col, width=w, anchor="w" if col != "actions" else "center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Dữ liệu mẫu (Mô phỏng từ ảnh SQL bạn gửi) ---
        # Lưu ý: Dữ liệu JSON trong ảnh SQL (dob, points...) đã được tách ra từng cột
        self.action_icons = "✏  🗑"
        data = [
            (1, "Nguyễn Văn A", "0900000001", "a@example.com", "20/05/1990", "1200", "Gold", "02/12/2025"),
            (2, "Guest", "", "", "", "0", "Standard", "03/12/2025"),
            (3, "Trần Thị B", "0912345678", "tranthib@gmail.com", "15/08/1998", "540", "Silver", "04/12/2025"),
        ]
        
        for item in data:
            movie_id = item[0] 

            display_values = item[0:] + (self.action_icons,)

            self.tree.insert("", tk.END, iid=movie_id, values=display_values)

        # Bắt sự kiện click
        self.tree.bind("<ButtonRelease-1>", self.on_action_click)

    def on_action_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        
        column = self.tree.identify_column(event.x)
        # Cột actions là cột thứ 9 (#9)
        if column == '#9': 
            item_id = self.tree.identify_row(event.y)
            bbox = self.tree.bbox(item_id, column)
            if bbox:
                # Logic chia đôi ô (Sửa | Xóa)
                cell_x, _, cell_width, _ = bbox
                relative_x = event.x - cell_x
                
                customer_name = self.tree.item(item_id, "values")[1]
                
                if relative_x < cell_width / 2:
                    messagebox.showinfo("Chỉnh sửa", f"Sửa thông tin khách: {customer_name}")
                else:
                    if messagebox.askyesno("Xác nhận", f"Xóa khách hàng {customer_name}?"):
                        self.tree.delete(item_id)
    
    