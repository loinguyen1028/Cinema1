import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime


class DatePickerPopup:
    def __init__(self, parent, current_date_str, on_confirm_callback, trigger_widget=None):
        self.parent = parent
        self.callback = on_confirm_callback
        self.current_date_str = current_date_str
        self.trigger_widget = trigger_widget

        self.show_calendar()

    def show_calendar(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Chọn ngày")

        # Định nghĩa kích thước cố định cho Popup
        POPUP_WIDTH = 300
        POPUP_HEIGHT = 280
        self.window.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}")

        self.window.grab_set()
        self.window.resizable(False, False)

        # --- TÍNH TOÁN VỊ TRÍ THÔNG MINH ---
        # Lấy kích thước màn hình máy tính
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = 0
        y = 0

        if self.trigger_widget:
            try:
                # Cập nhật thông tin widget mới nhất
                self.trigger_widget.update_idletasks()

                widget_x = self.trigger_widget.winfo_rootx()
                widget_y = self.trigger_widget.winfo_rooty()
                widget_height = self.trigger_widget.winfo_height()

                # 1. Mặc định: Căn trái theo widget, nằm ngay bên dưới
                x = widget_x
                y = widget_y + widget_height + 5

                # 2. Xử lý tràn mép PHẢI màn hình
                if x + POPUP_WIDTH > screen_width:
                    # Dịch sang trái để mép phải popup chạm mép phải màn hình (trừ 10px lề)
                    x = screen_width - POPUP_WIDTH - 10

                # 3. Xử lý tràn mép TRÁI màn hình (ít gặp, nhưng phòng hờ)
                if x < 0:
                    x = 10

                # 4. Xử lý tràn mép DƯỚI màn hình
                if y + POPUP_HEIGHT > screen_height:
                    # Lật ngược lên trên đầu widget
                    y = widget_y - POPUP_HEIGHT - 5

            except Exception as e:
                print(f"Lỗi tính vị trí: {e}")
                # Fallback: Hiện tại vị trí chuột
                x = self.parent.winfo_pointerx()
                y = self.parent.winfo_pointery()
        else:
            # Nếu không có widget kích hoạt, hiện tại vị trí chuột
            x = self.parent.winfo_pointerx()
            y = self.parent.winfo_pointery()

        # Áp dụng toạ độ đã tính toán (x, y là số dương)
        self.window.geometry(f"+{x}+{y}")

        # --- XỬ LÝ NGÀY MẶC ĐỊNH ---
        try:
            d, m, y_cal = map(int, self.current_date_str.split('/'))
        except:
            now = datetime.now()
            d, m, y_cal = now.day, now.month, now.year

        # --- VẼ LỊCH ---
        self.cal = Calendar(self.window, selectmode='day',
                            day=d, month=m, year=y_cal,
                            date_pattern='dd/mm/yyyy',
                            cursor="hand2",
                            weekendbackground="white",
                            weekendforeground="red"
                            )
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)

        btn_confirm = tk.Button(self.window, text="Chọn ngày này",
                                bg="#ff9800", fg="white", font=("Arial", 10, "bold"),
                                command=self.confirm_selection, relief="flat", cursor="hand2")
        btn_confirm.pack(pady=(0, 10), ipady=5, ipadx=10)

        self.cal.bind("<Double-1>", lambda e: self.confirm_selection())

    def confirm_selection(self):
        selected_date = self.cal.get_date()
        self.callback(selected_date)
        self.window.destroy()