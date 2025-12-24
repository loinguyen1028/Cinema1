import tkinter as tk
from tkinter import ttk, messagebox
from controllers.staff_controller import StaffController
from views.staff_dialog import StaffDialog


class StaffManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = StaffController()

        self.current_action_row = None
        self.action_buttons = []

        self.render()

    # =====================================================
    def render(self):
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444",
            "edit": "#2563eb",
            "selected": "#1e3a8a"
        }

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # ===== HEADER =====
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="👤 QUẢN LÝ NHÂN VIÊN",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="+ Thêm nhân viên",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=lambda: self.open_dialog("add")
        ).pack(side=tk.RIGHT)

        # ===== TABLE =====
        card = tk.Frame(container, bg=self.colors["card"])
        card.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=38,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["card"],
            foreground=self.colors["primary"],
            font=("Arial", 11, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", self.colors["selected"])],
            foreground=[("selected", "#ffffff")]
        )

        columns = (
            "id", "name", "gender", "dob",
            "phone", "email", "role", "start_date", "actions"
        )

        self.tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = [
            "ID", "Họ tên", "Giới tính", "Ngày sinh",
            "SĐT", "Email", "Chức vụ", "Ngày vào làm", "Thao tác"
        ]

        widths = [60, 180, 80, 100, 110, 220, 120, 120, 160]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("id", "gender", "actions") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=(col != "actions"))

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # EVENTS
        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_data()

    # =====================================================
    def load_data(self):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        staff_list = self.controller.get_all()

        for s in staff_list:
            extra = s.extra_info or {}

            self.tree.insert(
                "",
                tk.END,
                iid=s.user_id,
                values=(
                    s.user_id,
                    s.full_name,
                    extra.get("gender", ""),
                    extra.get("dob", ""),
                    extra.get("phone", ""),
                    extra.get("email", ""),
                    s.role.role_name if s.role else "N/A",
                    extra.get("start_date", ""),
                    ""
                )
            )

    # =====================================================
    # ===== ACTION BUTTON SYSTEM =====
    def create_action_buttons(self):
        base = {
            "font": ("Arial", 11),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_edit = tk.Button(
            self.tree,
            text="✏",
            bg=self.colors["edit"],
            fg="white",
            command=self.on_edit,
            **base
        )

        self.btn_delete = tk.Button(
            self.tree,
            text="🗑",
            bg=self.colors["danger"],
            fg="white",
            command=self.on_delete,
            **base
        )

        self.action_buttons = [self.btn_edit, self.btn_delete]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        self.current_action_row = selected[0]

        bbox = self.tree.bbox(self.current_action_row, "#9")
        if not bbox:
            return

        x, y, width, height = bbox
        part = width // 2

        for i, btn in enumerate(self.action_buttons):
            btn.place(
                x=x + i * part + 4,
                y=y + 4,
                width=part - 8,
                height=height - 8
            )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    # =====================================================
    # ===== ACTION HANDLERS =====
    def on_edit(self):
        if self.current_action_row:
            self.open_dialog("edit", self.current_action_row)

    def on_delete(self):
        if not self.current_action_row:
            return

        name = self.tree.item(self.current_action_row, "values")[1]
        if messagebox.askyesno("Xác nhận", f"Xóa nhân viên: {name}?"):
            success, msg = self.controller.delete(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)

    # =====================================================
    def open_dialog(self, mode, staff_id=None):
        StaffDialog(
            self.parent,
            self.controller,
            mode,
            staff_id,
            on_success=self.load_data
        )
