import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime


class DatePickerPopup:
    # --- CẬP NHẬT: Thêm tham số trigger_widget=None ---
    def __init__(self, parent, current_date_str, on_confirm_callback, trigger_widget=None):
        """
        parent: Cửa sổ cha
        current_date_str: Ngày hiện tại (vd: "25/12/2025")
        on_confirm_callback: Hàm callback chạy khi chọn xong
        trigger_widget: Widget đã gọi lịch (dùng để tính toán vị trí hiển thị)
        """
        self.parent = parent
        self.callback = on_confirm_callback
        self.current_date_str = current_date_str
        self.trigger_widget = trigger_widget

        self.show_calendar()

    def show_calendar(self):
        # Tạo cửa sổ con (Toplevel)
        self.window = tk.Toplevel(self.parent)
        self.window.title("Chọn ngày")
        self.window.geometry("300x280")
        self.window.grab_set()
        self.window.resizable(False, False)

        # --- LOGIC TÍNH TOÁN VỊ TRÍ HIỂN THỊ MỚI ---
        x = 0
        y = 0

        if self.trigger_widget:
            try:
                # Lấy toạ độ tuyệt đối của widget gọi lịch
                widget_x = self.trigger_widget.winfo_rootx()
                widget_y = self.trigger_widget.winfo_rooty()
                widget_height = self.trigger_widget.winfo_height()

                # Tính toán: X bằng mép trái widget, Y nằm ngay dưới đáy widget
                x = widget_x
                y = widget_y + widget_height + 2

                # Kiểm tra nếu lịch bị tràn ra khỏi màn hình dưới thì đẩy lên trên
                screen_height = self.window.winfo_screenheight()
                if y + 280 > screen_height:
                    y = widget_y - 280 - 2
            except:
                # Nếu lỗi lấy toạ độ widget thì dùng chuột
                x = self.parent.winfo_pointerx()
                y = self.parent.winfo_pointery()
        else:
            # Fallback: Hiện tại vị trí chuột nếu không truyền widget
            x = self.parent.winfo_pointerx()
            y = self.parent.winfo_pointery()

        self.window.geometry(f"+{x - 350}+{y}")

        # --- XỬ LÝ NGÀY MẶC ĐỊNH ---
        try:
            # Parse ngày từ chuỗi "dd/mm/yyyy"
            d, m, y_cal = map(int, self.current_date_str.split('/'))
        except:
            now = datetime.now()
            d, m, y_cal = now.day, now.month, now.year

        # --- WIDGET LỊCH ---
        self.cal = Calendar(self.window, selectmode='day',
                            day=d, month=m, year=y_cal,
                            date_pattern='dd/mm/yyyy',
                            cursor="hand2",
                            weekendbackground="white",
                            weekendforeground="red"
                            )
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)

        # --- NÚT XÁC NHẬN ---
        btn_confirm = tk.Button(self.window, text="Chọn ngày này",
                                bg="#ff9800", fg="white", font=("Arial", 10, "bold"),
                                command=self.confirm_selection, relief="flat", cursor="hand2")
        btn_confirm.pack(pady=(0, 10), ipady=5, ipadx=10)

        # Bắt sự kiện Double Click vào ngày để chọn nhanh
        self.cal.bind("<Double-1>", lambda e: self.confirm_selection())

    def confirm_selection(self):
        selected_date = self.cal.get_date()
        self.callback(selected_date)
        self.window.destroy()