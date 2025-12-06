import tkinter as tk
from tkinter import ttk, messagebox
from controllers.ticket_controller import TicketController


class TicketManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = TicketController()
        self.render()

    def render(self):
        # Layout
        content = tk.Frame(self.parent, bg="#f0f2f5")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Toolbar
        toolbar = tk.Frame(content, bg="#f0f2f5")
        toolbar.pack(fill=tk.X, pady=(0, 20))

        search_frame = tk.Frame(toolbar, bg="#f0f2f5")
        search_frame.pack(side=tk.LEFT)
        self.entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.entry_search.pack(side=tk.LEFT, ipady=3)
        self.entry_search.bind("<KeyRelease>", self.on_search)
        tk.Label(search_frame, text="🔍 Tìm theo Mã vé / SĐT", font=("Arial", 10), bg="#f0f2f5", fg="#666").pack(
            side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="🔄 Tải lại", bg="#5c6bc0", fg="white",
                  command=self.load_data).pack(side=tk.RIGHT)

        # Table
        table_frame = tk.Frame(content, bg="white", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        columns = ("id", "movie", "room", "seats", "customer", "date", "total", "actions")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers = ["Mã vé", "Phim", "Phòng", "Ghế", "Khách hàng", "Ngày đặt", "Tổng tiền", "Thao tác"]
        widths = [60, 200, 80, 150, 150, 150, 100, 100]

        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h, anchor="center")
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_click)

        self.load_data()

    def load_data(self):
        tickets = self.controller.get_all_tickets()
        self.update_table(tickets)

    def on_search(self, event):
        keyword = self.entry_search.get().strip()
        tickets = self.controller.search_tickets(keyword)
        self.update_table(tickets)

    def update_table(self, tickets):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for t in tickets:
            # Xử lý hiển thị
            movie_name = t.showtime.movie.title if t.showtime and t.showtime.movie else "N/A"
            room_name = t.showtime.room.room_name if t.showtime and t.showtime.room else "N/A"

            # Ghép danh sách ghế
            seat_list = [f"{ts.seat.seat_row}{ts.seat.seat_number}" for ts in t.ticket_seats]
            seat_str = ", ".join(seat_list)

            cus_info = f"{t.customer.name}\n({t.customer.phone})" if t.customer else "Khách vãng lai"
            date_str = t.booking_time.strftime("%d/%m %H:%M")
            total_str = f"{int(t.total_amount):,} đ"

            vals = (t.ticket_id, movie_name, room_name, seat_str, cus_info, date_str, total_str, "❌ Hủy vé")
            self.tree.insert("", tk.END, iid=t.ticket_id, values=vals)

    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return

        col = self.tree.identify_column(event.x)
        if col == '#8':  # Cột thao tác
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn HỦY vé #{item_id}?"):
                success, msg = self.controller.cancel_ticket(item_id)
                if success:
                    messagebox.showinfo("Thành công", msg)
                    self.load_data()
                else:
                    messagebox.showerror("Lỗi", msg)