# customers_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

class CustomersWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Quản lý khách hàng")
        self.geometry("700x400")

        # Form nhập
        form = tk.Frame(self)
        form.pack(fill=tk.X, pady=5)

        tk.Label(form, text="Tên:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(form, text="SĐT:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(form, text="Email:").grid(row=2, column=0, sticky="w", padx=5, pady=2)

        self.var_id = None
        self.entry_name = tk.Entry(form)
        self.entry_phone = tk.Entry(form)
        self.entry_email = tk.Entry(form)

        self.entry_name.grid(row=0, column=1, padx=5, pady=2)
        self.entry_phone.grid(row=1, column=1, padx=5, pady=2)
        self.entry_email.grid(row=2, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=0, column=2, rowspan=3, padx=10)

        tk.Button(btn_frame, text="Thêm mới", command=self.add_customer).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Cập nhật", command=self.update_customer).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Xóa", command=self.delete_customer).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Làm mới", command=self.clear_form).pack(fill=tk.X, pady=2)

        # Bảng
        self.tree = ttk.Treeview(self, columns=("id", "name", "phone", "email"),
                                 show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Tên")
        self.tree.heading("phone", text="SĐT")
        self.tree.heading("email", text="Email")
        self.tree.column("id", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_customers()

    def load_customers(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT customer_id, name, phone, email FROM customers ORDER BY customer_id")
            for cid, name, phone, email in cur.fetchall():
                self.tree.insert("", tk.END, values=(cid, name, phone, email))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def clear_form(self):
        self.var_id = None
        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        cid, name, phone, email = item["values"]
        self.var_id = cid
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, name)
        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, phone)
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, email)

    def add_customer(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()

        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Tên không được để trống")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO customers (name, phone, email)
                VALUES (%s, %s, %s)
            """, (name, phone, email))
            conn.commit()
            conn.close()
            self.load_customers()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def update_customer(self):
        if not self.var_id:
            messagebox.showwarning("Chọn khách", "Hãy chọn một khách hàng để sửa")
            return

        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()

        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Tên không được để trống")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE customers
                SET name=%s, phone=%s, email=%s
                WHERE customer_id=%s
            """, (name, phone, email, self.var_id))
            conn.commit()
            conn.close()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def delete_customer(self):
        if not self.var_id:
            messagebox.showwarning("Chọn khách", "Hãy chọn một khách hàng để xóa")
            return

        if not messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn xóa khách này?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM customers WHERE customer_id=%s",
                        (self.var_id,))
            conn.commit()
            conn.close()
            self.load_customers()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
