from dao.product_dao import ProductDAO
from dao.ticket_dao import TicketDAO
from dao.customer_dao import CustomerDAO

class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
        self.ticket_dao = TicketDAO()
        self.customer_dao = CustomerDAO()

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
    def process_direct_sale(self, user_id, total_amount, products_list, customer_id=None):
        if not products_list:
            return False, "Giỏ hàng trống!"

        try:
            success = self.ticket_dao.create_concession_transaction(user_id, total_amount, products_list, customer_id)

            if success:
                if customer_id:
                    self.customer_dao.update_membership(customer_id, total_amount)

                return True, "Thanh toán thành công!"
            else:
                return False, "Lỗi khi lưu giao dịch vào Database"

        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"

    def search_products(self, keyword, category):
        return self.dao.search_products(keyword, category)

    def get_categories(self):
        return self.dao.get_categories()