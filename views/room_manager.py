import tkinter as tk
from tkinter import ttk, messagebox
from controllers.room_controller import RoomController
from views.room_dialog import RoomDialog


class RoomManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = RoomController()

        # ===== STATE =====
        self.action_buttons = []
        self.current_action_row = None

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
            "edit": "#2563eb"
        }

        for w in self.parent.winfo_children():
            w.destroy()

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # ===== HEADER =====
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="🏢 QUẢN LÝ PHÒNG CHIẾU",
            font=("Arial", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["primary"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="+ Thêm phòng",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.open_add_dialog
        ).pack(side=tk.RIGHT)

        # ===== CARD =====
        card = tk.Frame(container, bg=self.colors["card"])
        card.pack(fill=tk.BOTH, expand=True)

        # ===== TREEVIEW STYLE =====
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=40,
            font=("Arial", 11),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["card"],
            foreground=self.colors["primary"],
            font=("Arial", 11, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#1e3a8a")],
            foreground=[("selected", "#ffffff")]
        )

        columns = ("room_id", "room_name", "capacity", "actions")
        self.tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headers = ["ID", "Tên phòng", "Sức chứa", "Thao tác"]
        widths = [70, 260, 120, 150]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("room_id", "capacity", "actions") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=(col != "actions"))

        self.tree.column("actions", stretch=False, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== EVENTS =====
        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_rooms()

    # =====================================================
    def load_rooms(self):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        rooms = self.controller.get_all_rooms()

        for room in rooms:
            self.tree.insert(
                "",
                tk.END,
                iid=room.room_id,
                values=(
                    room.room_id,
                    room.room_name,
                    room.capacity,
                    ""  # cell trống
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

        item_id = selected[0]
        self.current_action_row = item_id

        bbox = self.tree.bbox(item_id, "#4")
        if not bbox:
            return

        x, y, width, height = bbox
        part = width // 2

        for i, btn in enumerate(self.action_buttons):
            btn.place(
                x=x + i * part + 4,
                y=y + 5,
                width=part - 8,
                height=height - 10
            )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    # =====================================================
    # ===== ACTIONS =====
    def open_add_dialog(self):
        RoomDialog(
            self.parent,
            self.controller,
            mode="add",
            on_success=self.load_rooms
        )

    def on_edit(self):
        if self.current_action_row:
            RoomDialog(
                self.parent,
                self.controller,
                mode="edit",
                room_id=self.current_action_row,
                on_success=self.load_rooms
            )

    def on_delete(self):
        if not self.current_action_row:
            return

        if messagebox.askyesno(
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa phòng chiếu này?"
        ):
            success, msg = self.controller.delete_room(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_rooms()
            else:
                messagebox.showerror("Lỗi", msg)
