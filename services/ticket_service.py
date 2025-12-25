from dao.ticket_dao import TicketDAO
from dao.showtime_dao import ShowtimeDAO
from dao.customer_dao import CustomerDAO
from dao.product_dao import ProductDAO


class TicketService:
    def __init__(self):
        self.ticket_dao = TicketDAO()
        self.showtime_dao = ShowtimeDAO()
        self.customer_dao = CustomerDAO()
        self.product_dao = ProductDAO()


    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        all_showtimes = self.showtime_dao.filter_showtimes(date_str=date_str)
        grouped = {}
        for st in all_showtimes:
            m = st.movie
            if keyword and keyword.lower() not in m.title.lower(): continue
            m_genre = m.extra_info.get('genre', '') if m.extra_info else ""
            if genre != "Tất cả" and genre not in m_genre: continue

            if m.movie_id not in grouped:
                grouped[m.movie_id] = {'data': m, 'showtimes': []}
            grouped[m.movie_id]['showtimes'].append(st)
        return list(grouped.values())

    def get_showtime_detail(self, st_id):
        return self.showtime_dao.get_showtime_by_id(st_id)

    def get_products(self):
        return self.product_dao.get_all()

    def get_all_tickets(self):
        return self.ticket_dao.get_all_tickets()

    def search_tickets(self, kw):
        return self.ticket_dao.search_tickets(kw)



    def calculate_discount(self, customer_phone, type_selection):

        special_rates = {"Sinh viên": 0.20, "Trẻ em": 0.30, "Người cao tuổi": 0.20}
        special_percent = special_rates.get(type_selection, 0.0)

        customer = None
        member_percent = 0.0
        msg = ""


        if customer_phone:

            customer = self.customer_dao.get_by_phone(customer_phone)

            if customer:

                if customer.tier:

                    member_percent = float(customer.tier.discount_percent) / 100
                    level_name = customer.tier.tier_name
                else:
                    member_percent = 0.0
                    level_name = "Chưa xếp hạng"


                msg = f"Thành viên: {customer.name} ({level_name})"
            else:
                msg = "Khách vãng lai (SĐT không tồn tại)"


        final_percent = max(special_percent, member_percent)

        return customer, final_percent, msg

    def process_payment(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, points_used=0,
                        products_list=None):
        """Xử lý giao dịch thanh toán vé trọn gói"""
        if not seat_ids:
            return False, "Vui lòng chọn ít nhất 1 ghế!"


        if customer_id and points_used > 0:
            ok, msg_deduct = self.customer_dao.deduct_points(customer_id, points_used)
            if not ok: return False, msg_deduct


        success, msg = self.ticket_dao.create_ticket(
            showtime_id, user_id, seat_ids, total_amount,
            customer_id=customer_id,
            products_list=products_list
        )


        if success and customer_id:
            ok_add, point_msg = self.customer_dao.update_membership(customer_id, total_amount)
            if ok_add: msg += f"\n({point_msg})"
            if points_used > 0: msg += f"\n(Đã trừ {points_used} điểm)"

        return success, msg

    def cancel_ticket(self, ticket_id):
        return self.ticket_dao.delete_ticket(ticket_id)