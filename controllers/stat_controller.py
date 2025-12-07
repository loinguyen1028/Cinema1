from services.stat_service import StatService

class StatController:
    def __init__(self):
        self.service = StatService()

    def get_revenue_data(self):
        return self.service.get_revenue_chart_data()

    def get_monthly_revenue(self):
        return self.service.get_monthly_revenue_data()

    def get_top_movies(self):
        return self.service.get_top_movies_data()

    def get_top_products(self):
        return self.service.get_top_products_data()