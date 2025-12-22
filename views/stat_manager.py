import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
from datetime import datetime, timedelta
from controllers.stat_controller import StatsController


class StatManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = StatsController()

        self.render_filter_bar()

        # TẠO 3 TAB
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Tài chính (Doanh thu, Cơ cấu, Theo phòng)
        self.tab_finance = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_finance, text="1. Báo cáo Tài chính")

        # Tab 2: Hiệu suất (Top Phim, Top Sản phẩm)
        self.tab_performance = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_performance, text="2. Hiệu suất & Sản phẩm")

        # Tab 3: Khách hàng & Xu hướng (Thành viên, Khung giờ vàng)
        self.tab_customer = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_customer, text="3. Khách hàng & Xu hướng")

        self.load_data()
        self.pack(fill=tk.BOTH, expand=True)

    def render_filter_bar(self):
        bar = tk.Frame(self, bg="white", height=50)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="Từ ngày:", bg="white").pack(side=tk.LEFT, padx=5)
        self.e_start = tk.Entry(bar, width=12)
        self.e_start.pack(side=tk.LEFT)
        self.e_start.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        tk.Button(bar, text="📅", command=lambda: self.open_calendar(self.e_start)).pack(side=tk.LEFT)

        tk.Label(bar, text="Đến ngày:", bg="white").pack(side=tk.LEFT, padx=5)
        self.e_end = tk.Entry(bar, width=12)
        self.e_end.pack(side=tk.LEFT)
        self.e_end.insert(0, datetime.now().strftime('%Y-%m-%d'))
        tk.Button(bar, text="📅", command=lambda: self.open_calendar(self.e_end)).pack(side=tk.LEFT)

        tk.Button(bar, text="📊 Xem Báo Cáo", bg="#1976d2", fg="white", font=("Arial", 10, "bold"),
                  command=self.load_data).pack(side=tk.LEFT, padx=20)

    def open_calendar(self, entry):
        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode='day', date_pattern='y-mm-dd')
        cal.pack()
        tk.Button(top, text="Chọn",
                  command=lambda: [entry.delete(0, tk.END), entry.insert(0, cal.get_date()), top.destroy()]).pack()

    def load_data(self):
        try:
            start = datetime.strptime(self.e_start.get(), '%Y-%m-%d').date()
            end = datetime.strptime(self.e_end.get(), '%Y-%m-%d').date()
        except:
            messagebox.showerror("Lỗi", "Ngày không hợp lệ"); return

        # Xóa biểu đồ cũ
        for tab in [self.tab_finance, self.tab_performance, self.tab_customer]:
            for w in tab.winfo_children(): w.destroy()

        # --- VẼ TAB 1: TÀI CHÍNH ---
        self.draw_chart(self.tab_finance, self.controller.get_revenue_chart_data(start, end),
                        "Doanh thu tổng hợp (VNĐ)", "bar", tk.TOP, (8, 3))

        frame_bot_1 = tk.Frame(self.tab_finance, bg="white");
        frame_bot_1.pack(fill=tk.BOTH, expand=True)
        self.draw_pie_chart(frame_bot_1, self.controller.get_revenue_structure(start, end),
                            "Cơ cấu Doanh thu", ["Vé phim", "Bắp nước"], tk.LEFT)

        self.draw_chart(frame_bot_1, self.controller.get_revenue_by_room(start, end),
                        "Doanh thu theo Phòng chiếu", "barh", tk.RIGHT, (5, 3))

        # --- VẼ TAB 2: HIỆU SUẤT ---
        frame_top_2 = tk.Frame(self.tab_performance, bg="white");
        frame_top_2.pack(fill=tk.BOTH, expand=True)
        self.draw_chart(frame_top_2, [(d[0], d[2]) for d in self.controller.get_top_movies(start, end)],
                        "Top Phim (Doanh thu)", "barh", tk.LEFT, (5, 3))

        self.draw_chart(frame_top_2, self.controller.get_top_products(start, end),
                        "Top Sản phẩm (Số lượng)", "bar", tk.RIGHT, (5, 3))

        # --- VẼ TAB 3: KHÁCH HÀNG & KHUNG GIỜ ---
        for w in self.tab_customer.winfo_children(): w.destroy()

        # Khung chứa biểu đồ hàng trên
        frame_top_3 = tk.Frame(self.tab_customer, bg="white")
        frame_top_3.pack(fill=tk.BOTH, expand=True)

        # 1. Khung giờ vàng
        golden_data = self.controller.get_golden_hours(start, end)
        formatted_golden = [(f"{d[0]}h", d[1]) for d in golden_data]
        self.draw_chart(frame_top_3, formatted_golden, "Khung giờ vàng (Lượng vé bán)", "line", tk.LEFT, (5, 3))

        # 2. Tỷ lệ lấp đầy
        occupancy_data = self.controller.get_occupancy_rate(start, end)
        self.draw_chart(frame_top_3, occupancy_data, "Tỷ lệ lấp đầy theo Phim (%)", "bar", tk.RIGHT, (5,3))

        # Khung chứa biểu đồ hàng dưới
        frame_bot_3 = tk.Frame(self.tab_customer, bg="white")
        frame_bot_3.pack(fill=tk.BOTH, expand=True)

        # 3. Khách thành viên (SỬA LẠI DÒNG NÀY)
        mem_data = self.controller.get_customer_type_stats(start, end)
        self.draw_pie_chart(frame_bot_3, mem_data, "Tỷ lệ khách hàng", ["Thành viên", "Vãng lai"], tk.TOP)

    # --- HÀM VẼ TỔNG QUÁT (Giúp code gọn hơn) ---
    def draw_chart(self, parent, data, title, kind, side, figsize):
        if not data: return
        labels = [str(d[0]) for d in data]
        values = [d[1] for d in data]

        fig = Figure(figsize=figsize, dpi=100)
        ax = fig.add_subplot(111)

        # --- HÀM PHỤ: Đổi số thành chữ (1.000.000 -> 1M) ---
        def currency_formatter(x, pos):
            if x >= 1e9: return f'{x * 1e-9:.1f}B'  # Tỷ
            if x >= 1e6: return f'{x * 1e-6:.1f}M'  # Triệu
            if x >= 1e3: return f'{x * 1e-3:.0f}K'  # Nghìn
            return f'{x:.0f}'

        # ---------------------------------------------------

        if kind == "bar":
            # Cột đứng (Doanh thu ngày, Top SP)
            ax.bar(labels, values, color='#1976d2', width=0.5)

            # Áp dụng rút gọn cho trục Tiền (Trục dọc Y)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))

            # Xoay chữ trục Ngang (Tên SP/Ngày)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=9)

            # Chừa lề dưới cho tên dài
            fig.subplots_adjust(bottom=0.3, left=0.15)

        elif kind == "barh":
            # Cột ngang (Top Phim, Doanh thu Phòng)
            ax.barh(labels, values, color='#9c27b0')

            # Áp dụng rút gọn cho trục Tiền (Trục ngang X)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(currency_formatter))
            ax.tick_params(axis='y', labelsize=9)

            # Chừa lề trái cho tên Phim dài
            fig.subplots_adjust(left=0.35, bottom=0.15)

        elif kind == "line":
            # Đường (Khung giờ)
            ax.plot(labels, values, marker='o', color='#ff5722', linewidth=2)
            ax.grid(True, linestyle='--')

            if len(labels) > 10:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)

            fig.subplots_adjust(bottom=0.2)

        ax.set_title(title, fontsize=10)

        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(side=side, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def draw_pie_chart(self, parent, data, title, labels, side):
        if sum(data) == 0: return
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#4caf50', '#ff9800'])
        ax.set_title(title, fontsize=10)
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(side=side, fill=tk.BOTH, expand=True, padx=5, pady=5)