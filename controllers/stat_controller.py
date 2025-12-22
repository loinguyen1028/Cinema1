from dao.stat_dao import StatsDAO


class StatsController:
    def __init__(self):
        self.dao = StatsDAO()

    def get_revenue_chart_data(self, start, end):
        return self.dao.get_revenue_by_date_range(start, end)

    def get_revenue_structure(self, start, end):
        return self.dao.get_revenue_structure(start, end)

    def get_revenue_by_room(self, start, end):
        return self.dao.get_revenue_by_room(start, end)

    def get_top_movies(self, start, end):
        return self.dao.get_top_movies(start, end)

    def get_top_products(self, start, end):
        return self.dao.get_top_products(start, end)

    def get_golden_hours(self, start, end):
        return self.dao.get_golden_hours(start, end)

    def get_customer_type_stats(self, start, end):
        return self.dao.get_customer_type_stats(start, end)

    def get_occupancy_rate(self, start, end):
        return self.dao.get_occupancy_rate(start, end)