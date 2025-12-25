import tkinter as tk
from tkinter import messagebox


class RoomDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode="add", room_id=None, on_success=None):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.room_id = room_id
        self.on_success = on_success

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "card": "#1f2933",
            "primary": "#facc15",
            "text": "#e5e7eb",
            "muted": "#9ca3af",
            "danger": "#ef4444"
        }

        self.title("Thêm phòng chiếu" if mode == "add" else "Cập nhật phòng chiếu")
        self.geometry("440x460")
        self.config(bg=self.colors["bg"])
        self.resizable(True, True)
        self.grab_set()

        self.render_ui()

        if mode == "edit" and room_id:
            self.load_data()

    def render_ui(self):
        container = tk.Frame(
            self,
            bg=self.colors["card"],
            padx=30,
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

        label("Tên phòng chiếu")
        self.e_name = entry()

        label("Số hàng ghế (A-Z)")
        self.e_rows = entry()

        label("Số ghế mỗi hàng")
        self.e_seats_per_row = entry()

        tk.Button(
            container,
            text="💾 LƯU",
            bg=self.colors["primary"],
            fg="#000000",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2",
            command=self.save_action
        ).pack(pady=(10, 0))

    def load_data(self):
        room = self.controller.get_room_by_id(self.room_id)
        if room:
            self.e_name.insert(0, room.room_name)

            rows = len({s.seat_row for s in room.seats})
            seats_per_row = max(s.seat_number for s in room.seats)

            self.e_rows.insert(0, rows)
            self.e_seats_per_row.insert(0, seats_per_row)

    def save_action(self):
        name = self.e_name.get().strip()
        rows = self.e_rows.get().strip()
        seats_per_row = self.e_seats_per_row.get().strip()

        success, msg = self.controller.save_room(
            self.mode,
            self.room_id,
            name,
            rows,
            seats_per_row
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showwarning("Lỗi", msg)
