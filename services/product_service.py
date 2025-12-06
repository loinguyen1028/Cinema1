from dao.product_dao import ProductDAO
from dao.ticket_dao import TicketDAO  # Import thêm để xử lý bán hàng trực tiếp


class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
        self.ticket_dao = TicketDAO()

    def get_all(self):
        return self.dao.get_all()

    def get_detail(self, p_id):
        # DAO thường có hàm get_by_id, hãy chắc chắn ProductDAO có hàm này
        return self.dao.get_by_id(p_id)

    def save_product(self, mode, p_id, name, category, price, image_path):
        if not name: return False, "Tên sản phẩm thiếu"
        try:
            p_val = float(price)
            if p_val < 0: return False, "Giá không được âm"
        except:
            return False, "Giá phải là số"

        if mode == "add":
            return self.dao.add(name, category, p_val, image_path)
        else:
            return self.dao.update(p_id, name, category, p_val, image_path)

    def delete_product(self, p_id):
        return self.dao.delete(p_id)

    # Xử lý bán hàng trực tiếp (Đồ ăn)
    def process_direct_sale(self, user_id, total_amount, products_list):
        if not products_list:
            return False, "Giỏ hàng trống"

        # Gọi TicketDAO tạo hóa đơn loại "Bắp nước" (showtime_id=None)
        return self.ticket_dao.create_ticket(
            showtime_id=None,
            user_id=user_id,
            seat_ids=[],
            total_amount=total_amount,
            customer_id=None,
            products_list=products_list
        )

    def search_products(self, keyword, category):
        return self.dao.search_products(keyword, category)

    def get_categories(self):
        return self.dao.get_categories()