from dao.stat_dao import StatDAO
from datetime import datetime, timedelta


class StatService:
    def __init__(self):
        self.dao = StatDAO()

    def get_revenue_chart_data(self):
        data = self.dao.get_revenue_by_date(7)


        data_map = {d[0]: d[1] for d in data}

        dates = []
        revenues = []

        today = datetime.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            dates.append(day.strftime("%d/%m"))


            raw_val = data_map.get(day, 0)


            revenues.append(float(raw_val))

        return dates, revenues

    def get_monthly_revenue_data(self):
        current_year = datetime.now().year
        data = self.dao.get_monthly_revenue(current_year)


        data_map = {int(row[0]): row[1] for row in data}

        months = []
        revenues = []


        for i in range(1, 13):
            months.append(f"T{i}")

            raw_val = data_map.get(i, 0)
            revenues.append(float(raw_val))

        return months, revenues

    def get_top_movies_data(self):
        data = self.dao.get_top_movies()
        titles = []
        revenues = []

        for row in data:
            titles.append(row[0])

            revenues.append(float(row[1]))

        return titles, revenues

    def get_top_products_data(self):
        data = self.dao.get_top_products()
        names = []
        quantities = []

        for row in data:
            names.append(row[0])

            quantities.append(int(row[1]))

        return names, quantities