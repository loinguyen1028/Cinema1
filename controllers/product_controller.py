from dao.product_dao import ProductDAO


class ProductController:
    def __init__(self):
        self.dao = ProductDAO()

    def get_all(self):
        return self.dao.get_all()

    def save(self, mode, p_id, name, category, price, image_path):
        if not name: return False, "Tên không được rỗng"
        if not str(price).replace('.', '', 1).isdigit(): return False, "Giá phải là số"

        if mode == "add":
            return self.dao.add(name, category, float(price), image_path)
        else:
            return self.dao.update(p_id, name, category, float(price), image_path)

    def delete(self, p_id):
        return self.dao.delete(p_id)

    def get_detail(self, p_id):
        return self.dao.get_by_id(p_id)

    def process_direct_sale(self, user_id, total_amount, products_list):
        if not products_list:
            return False, "Giỏ hàng trống!"

        # Gọi TicketDAO với showtime_id = None, seat_ids = []
        return self.ticket_dao.create_ticket(
            showtime_id=None,
            user_id=user_id,
            seat_ids=[],
            total_amount=total_amount,
            customer_id=None,  # Tạm thời chưa tích điểm khách hàng ở đây (có thể nâng cấp sau)
            products_list=products_list
        )