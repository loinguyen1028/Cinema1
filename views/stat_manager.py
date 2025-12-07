import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from controllers.stat_controller import StatController


# Hàm phụ trợ: Đổi số thành dạng rút gọn (1.000.000 -> 1M)
def currency_formatter(x, pos):
    if x >= 1_000_000_000:
        return f'{x * 1e-9:.1f}B'
    elif x >= 1_000_000:
        return f'{x * 1e-6:.1f}M'  # M là Triệu
    elif x >= 1_000:
        return f'{x * 1e-3:.0f}k'
    return f'{int(x)}'


class StatManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.controller = StatController()

        # Cấu hình style chung cho matplotlib đẹp hơn
        plt.style.use('bmh')  # Style nền xám nhẹ, có lưới

        self.render()

    def render(self):
        plt.close('all')
        # Tạo Tab
        tab_control = ttk.Notebook(self.parent)

        self.tab_revenue = tk.Frame(tab_control, bg="#ffffff")
        self.tab_ranking = tk.Frame(tab_control, bg="#ffffff")

        tab_control.add(self.tab_revenue, text="📊 Báo cáo Doanh thu")
        tab_control.add(self.tab_ranking, text="🏆 Top Phim & Sản phẩm")

        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        self.render_revenue_tab(self.tab_revenue)
        self.draw_ranking_charts(self.tab_ranking)

    def render_revenue_tab(self, parent):
        frame_top = tk.Frame(parent, bg="white")
        frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame_bottom = tk.Frame(parent, bg="white")
        frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.draw_daily_chart(frame_top)
        self.draw_monthly_chart(frame_bottom)

    def draw_daily_chart(self, parent):
        dates, revenues = self.controller.get_revenue_data()

        fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)

        # Vẽ đường (Line chart)
        ax.plot(dates, revenues, marker='o', linestyle='-', color='#2962ff', linewidth=2.5, markersize=6)
        # Tô màu gradient bên dưới
        ax.fill_between(dates, revenues, color='#2962ff', alpha=0.15)

        ax.set_title("DOANH THU 7 NGÀY GẦN NHẤT", fontsize=11, fontweight='bold', color='#333')
        ax.grid(True, linestyle='--', alpha=0.5)

        # Format trục Y (Tiền) cho dễ đọc
        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # HIỆN SỐ TIỀN TRÊN ĐẦU CÁC ĐIỂM
        for i, txt in enumerate(revenues):
            if txt > 0:  # Chỉ hiện nếu có doanh thu
                ax.annotate(currency_formatter(txt, 0), (dates[i], revenues[i]),
                            textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, color='blue')

        # Chỉnh lề để không bị cắt chữ
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_monthly_chart(self, parent):
        months, revenues = self.controller.get_monthly_revenue()

        fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)

        # Vẽ cột (Bar chart)
        bars = ax.bar(months, revenues, color='#ff9100', width=0.6, edgecolor='white')

        ax.set_title("DOANH THU THEO THÁNG (Năm nay)", fontsize=11, fontweight='bold', color='#333')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

        # HIỆN SỐ TIỀN TRÊN ĐẦU CỘT
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        currency_formatter(height, 0),
                        ha='center', va='bottom', fontsize=9, fontweight='bold', color='#e65100')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_ranking_charts(self, parent):
        # Tăng khoảng cách padding cho frame chứa để thoáng hơn
        frame_movie = tk.Frame(parent, bg="white")
        frame_movie.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=20)

        frame_prod = tk.Frame(parent, bg="white")
        frame_prod.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)

        # --- 1. Top Phim (Biểu đồ Ngang) ---
        m_titles, m_revenues = self.controller.get_top_movies()

        # Xử lý tên phim quá dài: Cắt bớt và thêm "..."
        short_titles = [(t[:25] + '..') if len(t) > 25 else t for t in m_titles]

        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)

        # Đảo ngược list để phim doanh thu cao nhất nằm trên cùng
        y_pos = range(len(short_titles))

        # Vẽ thanh ngang (barh), màu xanh Teal hiện đại
        bars1 = ax1.barh(y_pos, m_revenues, color='#00897B', height=0.6)

        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(short_titles, fontsize=9)
        ax1.invert_yaxis()  # Đảo trục Y để số 1 lên đầu

        # Tiêu đề & Trục
        ax1.set_title("TOP 5 PHIM DOANH THU CAO", fontsize=11, fontweight='bold', color='#333', pad=15)
        ax1.xaxis.set_major_formatter(FuncFormatter(currency_formatter))
        ax1.grid(axis='x', linestyle='--', alpha=0.3)  # Chỉ hiện lưới dọc mờ

        # Xóa bớt khung viền (spines) cho thoáng
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Hiện số tiền bên phải thanh ngang
        for i, v in enumerate(m_revenues):
            ax1.text(v, i, f" {currency_formatter(v, 0)}",
                     va='center', fontsize=9, fontweight='bold', color='#004D40')

        plt.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_movie)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- 2. Top Sản phẩm (Chuyển sang Biểu đồ Ngang) ---
        p_names, p_qty = self.controller.get_top_products()

        # Xử lý tên sản phẩm dài
        short_p_names = [(n[:22] + '..') if len(n) > 22 else n for n in p_names]

        fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        y_pos2 = range(len(short_p_names))

        # Vẽ thanh ngang, màu Cam đậm (Warm color)
        bars2 = ax2.barh(y_pos2, p_qty, color='#F57C00', height=0.6)

        ax2.set_yticks(y_pos2)
        ax2.set_yticklabels(short_p_names, fontsize=9)
        ax2.invert_yaxis()  # Top 1 lên đầu

        ax2.set_title("TOP 5 SẢN PHẨM BÁN CHẠY", fontsize=11, fontweight='bold', color='#333', pad=15)
        ax2.grid(axis='x', linestyle='--', alpha=0.3)

        # Xóa khung viền thừa
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        # Hiện số lượng bên phải
        for i, v in enumerate(p_qty):
            ax2.text(v, i, f" {int(v)}",
                     va='center', fontsize=9, fontweight='bold', color='#E65100')

        plt.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_prod)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)