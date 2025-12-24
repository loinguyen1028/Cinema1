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

        # ===== THEME ĐỒNG BỘ =====
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444"
        }

        self.title("Thêm sản phẩm" if mode == "add" else "Cập nhật sản phẩm")
        self.geometry("520x620")
        self.config(bg=self.colors["bg"])
        self.resizable(False, False)
        self.grab_set()

        self.current_image_path = ""
        self.product_data = self.load_initial_data()

        self.render_ui()

    # ================= DATA =================
    def load_initial_data(self):
        data = {"name": "", "category": "Đồ ăn", "price": "0"}

        if self.mode == "edit" and self.product_id:
            p = self.controller.get_detail(self.product_id)
            if p:
                data["name"] = p.name
                data["category"] = p.category
                data["price"] = str(int(p.price))
                if p.image_path:
                    self.current_image_path = p.image_path
        return data

    # ================= UI =================
    def render_ui(self):
        container = tk.Frame(
            self,
            bg=self.colors["card"],
            padx=30,
            pady=25
        )
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            container,
            text=self.title(),
            font=("Arial", 16, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(anchor="w", pady=(0, 20))

        # Helpers
        def label(text):
            tk.Label(
                container,
                text=text,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=("Arial", 10)
            ).pack(anchor="w")

        def entry():
            e = tk.Entry(
                container,
                font=("Arial", 11),
                bg=self.colors["panel"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief="flat"
            )
            e.pack(fill=tk.X, ipady=6, pady=(4, 14))
            return e

        # ===== TÊN =====
        label("Tên sản phẩm")
        self.e_name = entry()
        self.e_name.insert(0, self.product_data["name"])

        # ===== LOẠI =====
        label("Loại sản phẩm")
        self.cbo_cat = ttk.Combobox(
            container,
            values=["Đồ ăn", "Nước uống", "Combo", "Quà tặng"],
            state="readonly",
            font=("Arial", 11)
        )
        self.cbo_cat.set(self.product_data["category"])
        self.cbo_cat.pack(fill=tk.X, ipady=4, pady=(4, 14))

        # ===== GIÁ =====
        label("Giá bán (VND)")
        self.e_price = entry()
        self.e_price.insert(0, self.product_data["price"])

        # ===== ẢNH =====
        label("Hình ảnh sản phẩm")

        img_frame = tk.Frame(container, bg=self.colors["card"])
        img_frame.pack(fill=tk.X, pady=(6, 20))

        self.lbl_img = tk.Label(
            img_frame,
            text="NO IMAGE",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            width=14,
            height=7
        )
        self.lbl_img.pack(side=tk.LEFT)

        tk.Button(
            img_frame,
            text="📂 Chọn ảnh",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 10, "bold"),
            padx=16,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.choose_image
        ).pack(side=tk.LEFT, padx=20, anchor="n")

        if self.current_image_path:
            self.load_image_to_label(self.current_image_path)

        # ===== BUTTON =====
        btn_frame = tk.Frame(container, bg=self.colors["card"])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        tk.Button(
            btn_frame,
            text="💾 LƯU",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.save_action
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            btn_frame,
            text="✖ HỦY",
            bg=self.colors["danger"],
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.destroy
        ).pack(side=tk.RIGHT)

    # ================= IMAGE =================
    def choose_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.current_image_path = file_path
            self.load_image_to_label(file_path)

    def load_image_to_label(self, path):
        if not path or not os.path.exists(path):
            return
        try:
            img = Image.open(path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=photo, text="", width=100, height=100)
            self.lbl_img.image = photo
        except Exception as e:
            print(f"Lỗi load ảnh: {e}")

    # ================= SAVE =================
    def save_action(self):
        name = self.e_name.get().strip()
        cat = self.cbo_cat.get()
        price = self.e_price.get().strip()
        img = self.current_image_path

        success, msg = self.controller.save(
            self.mode,
            self.product_id,
            name,
            cat,
            price,
            img
        )

        if success:
            messagebox.showinfo("Thành công", "Lưu sản phẩm thành công!")
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)
