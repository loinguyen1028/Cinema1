import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

class DatePickerPopup:
    def __init__(self, parent, current_date_str, on_confirm_callback):
        """
        parent: Cửa sổ cha (để popup hiện lên trên)
        current_date_str: Ngày hiện tại đang chọn (để set mặc định cho lịch)
        on_confirm_callback: Hàm sẽ chạy khi người dùng chốt ngày (nhận vào 1 tham số là ngày mới)
        """
        self.parent = parent
        self.callback = on_confirm_callback
        self.current_date_str = current_date_str
        
        self.show_calendar()

    def show_calendar(self):
        # Tạo cửa sổ con (Toplevel)
        self.window = tk.Toplevel(self.parent)
        self.window.title("Chọn ngày")
        self.window.geometry("300x280")
        self.window.grab_set() # Chặn tương tác với cửa sổ chính khi đang mở lịch

        # Hiện lịch ngay tại vị trí chuột (UX tốt)
        try:
            x = self.parent.winfo_pointerx()
            y = self.parent.winfo_pointery()
            self.window.geometry(f"+{x}+{y}")
        except:
            pass

        # Xử lý ngày mặc định
        try:
            d, m, y = map(int, self.current_date_str.split('/'))
        except:
            now = datetime.now()
            d, m, y = now.day, now.month, now.year

        # Widget Lịch
        self.cal = Calendar(self.window, selectmode='day', 
                            day=d, month=m, year=y, 
                            date_pattern='dd/mm/yyyy',
                            cursor="hand2")
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Nút xác nhận
        btn_confirm = tk.Button(self.window, text="Chọn ngày này", 
                                bg="#ff9800", fg="white", font=("Arial", 10, "bold"),
                                command=self.confirm_selection, relief="flat", cursor="hand2")
        btn_confirm.pack(pady=(0, 10), ipady=5, ipadx=10)

        # Bind double click
        self.cal.bind("<Double-1>", lambda e: self.confirm_selection())

    def confirm_selection(self):
        # 1. Lấy ngày
        selected_date = self.cal.get_date()
        
        # 2. Gửi ngày về cho hàm callback ở file gốc
        self.callback(selected_date)
        
        # 3. Đóng lịch
        self.window.destroy()