import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


class ConcessionDialog(tk.Toplevel):
    def __init__(self, parent, controller, initial_selection=None, on_confirm=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_products = {k: v.copy() for k, v in initial_selection.items()} if initial_selection else {}
        self.on_confirm = on_confirm

        self.title("Menu Bắp Nước")
        self.geometry("1100x700")
        self.config(bg="#f0f2f5")
        self.grab_set()

        self.all_products = self.controller.get_products()

        categories_set = set(p.category for p in self.all_products if p.category)
        self.categories = ["Tất cả"] + sorted(list(categories_set))
        self.current_category = "Tất cả"

        self.render_layout()
        self.render_categories()
        self.render_products()

    def render_layout(self):
        header_frame = tk.Frame(self, bg="#0f1746", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            header_frame,
            text="MENU ĐỒ ĂN & THỨC UỐNG",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#0f1746"
        ).pack(side=tk.LEFT, padx=20)

        self.lbl_total = tk.Label(
            header_frame,
            text="Đã chọn: 0đ",
            font=("Arial", 12, "bold"),
            fg="#ff9800",
            bg="#0f1746"
        )
        self.lbl_total.pack(side=tk.RIGHT, padx=20)

        main_body = tk.Frame(self, bg="#f0f2f5")
        main_body.pack(fill=tk.BOTH, expand=True)

        self.cat_frame = tk.Frame(main_body, bg="white", width=220)
        self.cat_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.cat_frame.pack_propagate(False)

        tk.Label(
            self.cat_frame,
            text="DANH MỤC",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#555"
        ).pack(pady=(20, 10))

        right_frame = tk.Frame(main_body, bg="#f0f2f5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(right_frame, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)

        self.product_grid = tk.Frame(self.canvas, bg="#f0f2f5")

        self.product_grid.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.product_grid, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="white", pady=15)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            btn_frame,
            text="Hủy bỏ",
            bg="#eee",
            width=12,
            relief="flat",
            font=("Arial", 10),
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            btn_frame,
            text="Xác nhận chọn",
            bg="#1976d2",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            relief="flat",
            command=self.confirm_action
        ).pack(side=tk.RIGHT, padx=10)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def render_categories(self):
        for widget in self.cat_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        self.cat_buttons = {}

        for cat in self.categories:
            btn = tk.Button(
                self.cat_frame,
                text=cat,
                font=("Arial", 11),
                bg="white",
                fg="#333",
                relief="flat",
                anchor="w",
                padx=20,
                pady=10,
                activebackground="#e3f2fd",
                cursor="hand2",
                command=lambda c=cat: self.switch_category(c)
            )
            btn.pack(fill=tk.X, pady=2)
            self.cat_buttons[cat] = btn

        self.highlight_category()

    def switch_category(self, category):
        self.current_category = category
        self.highlight_category()
        self.render_products()

    def highlight_category(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.current_category:
                btn.config(bg="#1976d2", fg="white", font=("Arial", 11, "bold"))
            else:
                btn.config(bg="white", fg="#333", font=("Arial", 11, "normal"))

    def render_products(self):
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        if self.current_category == "Tất cả":
            display_products = self.all_products
        else:
            display_products = [p for p in self.all_products if p.category == self.current_category]

        COLUMNS = 4

        for idx, product in enumerate(display_products):
            row = idx // COLUMNS
            col = idx % COLUMNS
            self.create_product_card(product, row, col)

        self.update_total_label()

    def create_product_card(self, product, row, col):
        card = tk.Frame(self.product_grid, bg="white", bd=1, relief="solid")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        self.product_grid.grid_columnconfigure(col, weight=1)

        img_frame = tk.Frame(card, bg="white", height=140)
        img_frame.pack(fill=tk.X)
        img_frame.pack_propagate(False)

        lbl_img = tk.Label(img_frame, text="NO IMAGE", bg="#eee", fg="#999")
        lbl_img.pack(fill=tk.BOTH, expand=True)

        if product.image_path and os.path.exists(product.image_path):
            try:
                img = Image.open(product.image_path)
                img = img.resize((140, 140), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl_img.config(image=photo, text="", bg="white")
                lbl_img.image = photo
            except:
                pass

        info_frame = tk.Frame(card, bg="white", pady=5)
        info_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            info_frame,
            text=product.name,
            font=("Arial", 10, "bold"),
            bg="white",
            wraplength=130,
            anchor="w"
        ).pack(fill=tk.X)

        tk.Label(
            info_frame,
            text=f"{int(product.price):,} đ",
            font=("Arial", 11),
            fg="#e65100",
            bg="white",
            anchor="w"
        ).pack(fill=tk.X)

        ctrl_frame = tk.Frame(card, bg="white", pady=10)
        ctrl_frame.pack(fill=tk.X)

        current_qty = self.selected_products.get(product.product_id, {}).get("qty", 0)
        var_qty = tk.IntVar(value=current_qty)

        def change_qty(delta):
            new_q = var_qty.get() + delta
            if new_q < 0:
                new_q = 0
            if new_q > 50:
                return

            var_qty.set(new_q)

            if new_q > 0:
                self.selected_products[product.product_id] = {"obj": product, "qty": new_q}
                card.config(bd=2, relief="solid", highlightbackground="#1976d2", highlightthickness=2)
            else:
                self.selected_products.pop(product.product_id, None)
                card.config(bd=1, relief="solid", highlightthickness=0)

            self.update_total_label()

        tk.Button(
            ctrl_frame,
            text="-",
            font=("Arial", 12, "bold"),
            width=3,
            bg="#eee",
            relief="flat",
            command=lambda: change_qty(-1)
        ).pack(side=tk.LEFT, padx=(15, 5))

        tk.Label(
            ctrl_frame,
            textvariable=var_qty,
            font=("Arial", 12, "bold"),
            bg="white",
            width=3
        ).pack(side=tk.LEFT)

        tk.Button(
            ctrl_frame,
            text="+",
            font=("Arial", 12, "bold"),
            width=3,
            bg="#1976d2",
            fg="white",
            relief="flat",
            command=lambda: change_qty(1)
        ).pack(side=tk.RIGHT, padx=(5, 15))

        if current_qty > 0:
            card.config(highlightbackground="#1976d2", highlightthickness=2)

    def update_total_label(self):
        total = sum(i["obj"].price * i["qty"] for i in self.selected_products.values())
        count = sum(i["qty"] for i in self.selected_products.values())
        self.lbl_total.config(text=f"Đã chọn ({count} món): {int(total):,} đ")

    def confirm_action(self):
        if self.on_confirm:
            self.on_confirm(self.selected_products)
        self.destroy()
