from dao.stat_dao import StatDAO
from datetime import datetime, timedelta


class StatService:
    def __init__(self):
        self.dao = StatDAO()

    def get_revenue_chart_data(self):
        data = self.dao.get_revenue_by_date(7)

        # Tạo dict map: {date: total}
        data_map = {d[0]: d[1] for d in data}

        dates = []
        revenues = []

        today = datetime.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            dates.append(day.strftime("%d/%m"))

            # Lấy giá trị, mặc định là 0 nếu không có
            raw_val = data_map.get(day, 0)

            # --- SỬA LỖI TẠI ĐÂY: Ép kiểu Decimal sang float ---
            revenues.append(float(raw_val))

        return dates, revenues

    def get_monthly_revenue_data(self):
        current_year = datetime.now().year
        data = self.dao.get_monthly_revenue(current_year)

        # Tạo dict: {tháng: tiền} (Ví dụ: {1: 500000, 2: 1000000})
        # Lưu ý: row[0] trả về float/decimal nên cần ép về int làm key
        data_map = {int(row[0]): row[1] for row in data}

        months = []
        revenues = []

        # Loop từ tháng 1 đến 12
        for i in range(1, 13):
            months.append(f"T{i}")  # Nhãn trục hoành: T1, T2...

            raw_val = data_map.get(i, 0)  # Nếu tháng i không có doanh thu thì lấy 0
            revenues.append(float(raw_val))  # Ép kiểu float cho matplotlib

        return months, revenues

    def get_top_movies_data(self):
        data = self.dao.get_top_movies()
        titles = []
        revenues = []

        for row in data:
            titles.append(row[0])
            # --- SỬA LỖI TẠI ĐÂY: Ép kiểu Decimal sang float ---
            revenues.append(float(row[1]))

        return titles, revenues

    def get_top_products_data(self):
        data = self.dao.get_top_products()
        names = []
        quantities = []

        for row in data:
            names.append(row[0])
            # --- SỬA LỖI TẠI ĐÂY: Ép kiểu sang int hoặc float ---
            quantities.append(int(row[1]))  # Số lượng thì dùng int

        return names, quantities