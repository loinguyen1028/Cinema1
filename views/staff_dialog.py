import tkinter as tk
from tkinter import ttk, messagebox
from views.date_picker_popup import DatePickerPopup


class StaffDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", staff_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.staff_id = staff_id
        self.on_success = on_success

        self.colors = {
            "bg": "#0f172a",
            "card": "#1f2933",
            "panel": "#111827",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444"
        }

        self.title("Thêm nhân viên" if mode == "add" else "Cập nhật nhân viên")
        self.geometry("600x900")
        self.config(bg=self.colors["bg"])
        self.resizable(True, True)
        self.grab_set()

        self.roles_list = self.controller.get_roles()
        self.role_map = {r.role_name: r.role_id for r in self.roles_list}

        self.render_ui()

        if mode == "edit" and staff_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(
            self,
            bg=self.colors["card"],
            padx=35,
            pady=25
        )
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text=self.title(),
            font=("Arial", 16, "bold"),
            bg=self.colors["card"],
            fg=self.colors["primary"]
        ).pack(anchor="w", pady=(0, 20))

        def label(text):
            tk.Label(
                container,
                text=text,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=("Arial", 10)
            ).pack(anchor="w")

        def entry(parent=container):
            e = tk.Entry(
                parent,
                font=("Arial", 11),
                bg=self.colors["panel"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief="flat"
            )
            e.pack(fill=tk.X, ipady=6, pady=(4, 14))
            return e

        label("Họ và tên")
        self.e_name = entry()

        label("Giới tính")
        self.cbo_gender = ttk.Combobox(
            container,
            values=["Nam", "Nữ", "Khác"],
            state="readonly",
            font=("Arial", 11)
        )
        self.cbo_gender.current(0)
        self.cbo_gender.pack(fill=tk.X, ipady=4, pady=(4, 14))

        label("Ngày sinh")
        f_dob = tk.Frame(container, bg=self.colors["card"])
        f_dob.pack(fill=tk.X, pady=(4, 14))
        self.e_dob = entry(f_dob)
        self.create_calendar_btn(f_dob, self.e_dob)

        label("Số điện thoại")
        self.e_phone = entry()

        label("Email")
        self.e_email = entry()

        label("Ngày bắt đầu làm việc")
        f_start = tk.Frame(container, bg=self.colors["card"])
        f_start.pack(fill=tk.X, pady=(4, 14))
        self.e_start_date = entry(f_start)
        self.create_calendar_btn(f_start, self.e_start_date)

        acc_frame = tk.LabelFrame(
            container,
            text="Thông tin đăng nhập",
            bg=self.colors["card"],
            fg=self.colors["primary"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        acc_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            acc_frame,
            text="Tên tài khoản",
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="w")

        self.e_username = tk.Entry(
            acc_frame,
            font=("Arial", 11),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat"
        )
        self.e_username.pack(fill=tk.X, ipady=6, pady=(4, 14))

        tk.Label(
            acc_frame,
            text="Quyền hạn (Role)",
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(anchor="w")

        self.cbo_role = ttk.Combobox(
            acc_frame,
            values=list(self.role_map.keys()),
            state="readonly",
            font=("Arial", 11)
        )
        if self.role_map:
            self.cbo_role.current(0)
        self.cbo_role.pack(fill=tk.X, ipady=4)

        btn_frame = tk.Frame(container, bg=self.colors["card"])
        btn_frame.pack(fill=tk.X, pady=(20, 0))

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

    def create_calendar_btn(self, parent, entry_widget):
        def open_cal(e):
            DatePickerPopup(
                self,
                entry_widget.get(),
                lambda d: (
                    entry_widget.delete(0, tk.END),
                    entry_widget.insert(0, d)
                ),
                trigger_widget=entry_widget
            )

        tk.Label(
            parent,
            text="📅",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            cursor="hand2",
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=6)

        entry_widget.bind("<Button-1>", open_cal)

    def load_data(self):
        staff = self.controller.get_detail(self.staff_id)
        extra = staff.extra_info if staff.extra_info else {}

        self.e_name.insert(0, extra.get("name", ""))
        self.e_phone.insert(0, extra.get("phone", ""))
        self.e_email.insert(0, extra.get("email", ""))
        self.e_dob.insert(0, extra.get("dob", ""))
        self.e_start_date.insert(0, extra.get("start_date", ""))
        self.cbo_gender.set(extra.get("gender", "Nam"))

        if staff.role:
            self.cbo_role.set(staff.role.role_name)

        self.e_username.insert(0, staff.username)
        self.e_username.config(state="readonly")

    def save_action(self):
        role_name = self.cbo_role.get()
        role_id = self.role_map.get(role_name)

        data = {
            "name": self.e_name.get().strip(),
            "gender": self.cbo_gender.get(),
            "dob": self.e_dob.get(),
            "phone": self.e_phone.get().strip(),
            "email": self.e_email.get().strip(),
            "start_date": self.e_start_date.get(),
            "username": self.e_username.get().strip(),
            "role_id": role_id
        }

        success, msg = self.controller.save(self.mode, self.staff_id, data)

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)
