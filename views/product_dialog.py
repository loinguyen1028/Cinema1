import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os


class ProductDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", product_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.product_id = product_id
        self.on_success = on_success

        self.title("Thêm sản phẩm" if mode == "add" else "Cập nhật sản phẩm")
        self.geometry("500x600")
        self.config(bg="#f5f6f8")
        self.grab_set()

        self.current_image_path = ""
        self.product_data = self.load_initial_data()  # Load dữ liệu trước khi vẽ UI

        self.render_ui()

    def load_initial_data(self):
        data = {"name": "", "category": "Đồ ăn", "price": "0"}

        if self.mode == "edit" and self.product_id:
            # --- SỬA LỖI TẠI ĐÂY: Gọi controller lấy chi tiết ---
            p = self.controller.get_detail(self.product_id)
            if p:
                data["name"] = p.name
                data["category"] = p.category
                data["price"] = str(int(p.price))
                if p.image_path:
                    self.current_image_path = p.image_path
        return data

    def render_ui(self):
        container = tk.Frame(self, bg="#f5f6f8", padx=30, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text=self.title(), font=("Arial", 16, "bold"), bg="#f5f6f8", fg="#333").pack(anchor="w",
                                                                                                         pady=(0, 20))

        # 1. Tên sản phẩm
        tk.Label(container, text="Tên sản phẩm", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_name = tk.Entry(container, font=("Arial", 11))
        self.e_name.insert(0, self.product_data["name"])  # Đổ dữ liệu vào
        self.e_name.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 2. Loại (Combobox)
        tk.Label(container, text="Loại", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.cbo_cat = ttk.Combobox(container, values=["Đồ ăn", "Nước uống", "Combo", "Quà tặng"], font=("Arial", 11),
                                    state="readonly")
        self.cbo_cat.set(self.product_data["category"])  # Đổ dữ liệu vào
        self.cbo_cat.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 3. Giá
        tk.Label(container, text="Giá bán (VND)", bg="#f5f6f8", fg="#555").pack(anchor="w")
        self.e_price = tk.Entry(container, font=("Arial", 11))
        self.e_price.insert(0, self.product_data["price"])  # Đổ dữ liệu vào
        self.e_price.pack(fill=tk.X, ipady=4, pady=(0, 10))

        # 4. Ảnh minh họa
        tk.Label(container, text="Hình ảnh", bg="#f5f6f8", fg="#555").pack(anchor="w")

        img_frame = tk.Frame(container, bg="#f5f6f8")
        img_frame.pack(fill=tk.X, pady=5)

        self.lbl_img = tk.Label(img_frame, text="[ IMG ]", bg="#ddd", width=15, height=8)
        self.lbl_img.pack(side=tk.LEFT)

        tk.Button(img_frame, text="📂 Chọn ảnh", bg="#5c6bc0", fg="white",
                  command=self.choose_image).pack(side=tk.LEFT, padx=20, anchor="n")

        # --- QUAN TRỌNG: Load ảnh cũ lên nếu có ---
        if self.current_image_path:
            self.load_image_to_label(self.current_image_path)

        # Nút Hành động
        btn_frame = tk.Frame(container, bg="#f5f6f8", pady=20)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(btn_frame, text="Hủy", bg="#ff5722", fg="white", font=("Arial", 10, "bold"),
                  width=10, relief="flat", command=self.destroy).pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="Lưu", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                  width=10, relief="flat", command=self.save_action).pack(side=tk.RIGHT)

    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.current_image_path = file_path
            self.load_image_to_label(file_path)

    def load_image_to_label(self, path):
        if not path or not os.path.exists(path): return
        try:
            img = Image.open(path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=photo, text="", width=100, height=100)
            self.lbl_img.image = photo
        except Exception as e:
            print(f"Lỗi load ảnh: {e}")

    def save_action(self):
        name = self.e_name.get().strip()
        cat = self.cbo_cat.get()
        price = self.e_price.get().strip()
        img = self.current_image_path

        success, msg = self.controller.save(self.mode, self.product_id, name, cat, price, img)

        if success:
            messagebox.showinfo("Thành công", "Lưu sản phẩm thành công!")
            if self.on_success: self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)