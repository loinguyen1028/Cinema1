from services.product_service import ProductService
from dao.ticket_dao import TicketDAO

class ProductController:
    def __init__(self):
        self.service = ProductService()

    def get_all(self):
        return self.service.get_all()

    def get_detail(self, p_id):
        return self.service.get_detail(p_id)

    def save(self, mode, p_id, name, category, price, image_path):
        return self.service.save_product(mode, p_id, name, category, price, image_path)

    def delete(self, p_id):
        return self.service.delete_product(p_id)


    def process_direct_sale(self, user_id, total_amount, products_list, customer_id=None):
        ticket_dao = TicketDAO()
        return ticket_dao.create_concession_transaction(user_id, total_amount, products_list, customer_id)

    def search(self, keyword, category):
        return self.service.search_products(keyword, category)

    def get_categories(self):
        return self.service.get_categories()