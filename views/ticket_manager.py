import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController


class TicketManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = TicketController()

        # ===== STATE =====
        self.action_buttons = []
        self.current_action_row = None

        # ===== THEME =====
        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444",
            "selected": "#334155"
        }

        self.render()

    # =====================================================
    def render(self):
        for w in self.parent.winfo_children():
            w.destroy()

        container = tk.Frame(self.parent, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        # ================= HEADER =================
        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 18))

        tk.Label(
            header,
            text="🎟 QUẢN LÝ VÉ ĐÃ ĐẶT",
            font=("Arial", 18, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["bg"]
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="🔄 Tải lại",
            bg=self.colors["primary"],
            fg="#000",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.load_data
        ).pack(side=tk.RIGHT)

        # ================= TOOLBAR =================
        toolbar = tk.Frame(container, bg=self.colors["card"], padx=15, pady=12)
        toolbar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            toolbar,
            text="🔍 Tìm mã vé / SĐT:",
            font=("Arial", 11),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(side=tk.LEFT)

        self.entry_search = tk.Entry(toolbar, width=36, font=("Arial", 11), relief="flat")
        self.entry_search.pack(side=tk.LEFT, padx=10, ipady=6)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # ================= CARD =================
        card = tk.Frame(container, bg=self.colors["card"])
        card.pack(fill=tk.BOTH, expand=True)

        # ================= TABLE STYLE =================
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=44,
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
            background=[("selected", self.colors["selected"])],
            foreground=[("selected", "#ffffff")]
        )

        # ================= TABLE =================
        columns = (
            "id", "movie", "room", "seats",
            "customer", "date", "total", "actions"
        )

        self.tree = ttk.Treeview(card, columns=columns, show="headings", selectmode="browse")

        headers = [
            "Mã vé", "Phim", "Phòng", "Ghế",
            "Khách hàng", "Ngày đặt", "Tổng tiền", "Thao tác"
        ]
        widths = [80, 220, 90, 220, 220, 140, 130, 120]

        for col, h, w in zip(columns, headers, widths):
            anchor = "center" if col in ("id", "room", "date", "total", "actions") else "w"
            self.tree.heading(col, text=h, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=(col != "actions"))

        self.tree.column("actions", stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ================= EVENTS =================
        self.tree.bind("<<TreeviewSelect>>", self.show_action_buttons)
        self.tree.bind("<Button-1>", lambda e: self.hide_action_buttons())
        self.tree.bind("<MouseWheel>", lambda e: self.hide_action_buttons())
        self.tree.bind("<Configure>", lambda e: self.hide_action_buttons())

        self.create_action_buttons()
        self.load_data()

    # =====================================================
    # ================= DATA =================
    def load_data(self):
        self.hide_action_buttons()
        self.tree.delete(*self.tree.get_children())

        tickets = self.controller.get_all_tickets()

        for t in tickets:
            movie = t.showtime.movie.title if t.showtime and t.showtime.movie else "N/A"
            room = t.showtime.room.room_name if t.showtime and t.showtime.room else "N/A"
            seats = ", ".join(f"{s.seat.seat_row}{s.seat.seat_number}" for s in t.ticket_seats)
            customer = (
                f"{t.customer.name} ({t.customer.phone})"
                if t.customer else "Khách vãng lai"
            )
            date = t.booking_time.strftime("%d/%m %H:%M")
            total = f"{int(t.total_amount):,} đ"

            self.tree.insert(
                "",
                tk.END,
                iid=t.ticket_id,
                values=(t.ticket_id, movie, room, seats, customer, date, total, "")
            )

    def on_search(self, event=None):
        keyword = self.entry_search.get().strip()
        tickets = self.controller.search_tickets(keyword)
        self.load_data()
        self.update_table(tickets)

    def update_table(self, tickets):
        self.tree.delete(*self.tree.get_children())
        for t in tickets:
            self.tree.insert("", tk.END, iid=t.ticket_id, values=(t.ticket_id, "..."))

    # =====================================================
    # ================= ACTION BUTTON SYSTEM =================
    def create_action_buttons(self):
        base = {
            "font": ("Arial", 11),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2"
        }

        self.btn_delete = tk.Button(
            self.tree,
            text="🗑",
            bg=self.colors["danger"],
            fg="white",
            command=self.on_delete,
            **base
        )

        self.action_buttons = [self.btn_delete]

    def show_action_buttons(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        self.current_action_row = item_id

        bbox = self.tree.bbox(item_id, "#8")
        if not bbox:
            return

        x, y, width, height = bbox
        self.btn_delete.place(
            x=x + 6,
            y=y + 6,
            width=width - 12,
            height=height - 12
        )

    def hide_action_buttons(self):
        for btn in self.action_buttons:
            btn.place_forget()

    # =====================================================
    # ================= ACTION =================
    def on_delete(self):
        if not self.current_action_row:
            return

        if messagebox.askyesno(
            "Xác nhận",
            f"Bạn chắc chắn muốn HỦY vé #{self.current_action_row}?"
        ):
            success, msg = self.controller.cancel_ticket(self.current_action_row)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)
