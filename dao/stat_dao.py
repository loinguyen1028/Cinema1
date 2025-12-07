from sqlalchemy import func, desc, cast, Date
from db import db
from models import Ticket, TicketProduct, Product, Showtime, Movie
from datetime import datetime, timedelta


class StatDAO:
    def get_revenue_by_date(self, days=7):
        """Lấy doanh thu theo ngày trong khoảng `days` ngày gần nhất"""
        session = db.get_session()
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)

            # Query: Group by Ngày, Sum Tổng tiền
            results = session.query(
                cast(Ticket.booking_time, Date).label('date'),
                func.sum(Ticket.total_amount).label('total')
            ).filter(
                Ticket.status != 'cancelled',  # Không tính vé hủy
                cast(Ticket.booking_time, Date) >= start_date
            ).group_by(
                cast(Ticket.booking_time, Date)
            ).order_by(
                cast(Ticket.booking_time, Date)
            ).all()

            return results  # List of (date, total)
        finally:
            session.close()

    def get_monthly_revenue(self, year):
        session = db.get_session()
        try:
            # Query: Group by Tháng, Sum Tổng tiền
            results = session.query(
                func.extract('month', Ticket.booking_time).label('month'),
                func.sum(Ticket.total_amount).label('total')
            ).filter(
                Ticket.status != 'cancelled',
                func.extract('year', Ticket.booking_time) == year
            ).group_by(
                func.extract('month', Ticket.booking_time)
            ).order_by('month').all()

            return results  # List [(tháng, tổng tiền), ...]
        finally:
            session.close()

    def get_top_movies(self, limit=5):
        """Top phim có doanh thu cao nhất"""
        session = db.get_session()
        try:
            # Join: Ticket -> Showtime -> Movie
            results = session.query(
                Movie.title,
                func.sum(Ticket.total_amount).label('revenue')
            ).join(Showtime, Ticket.showtime_id == Showtime.showtime_id) \
                .join(Movie, Showtime.movie_id == Movie.movie_id) \
                .filter(Ticket.status != 'cancelled') \
                .group_by(Movie.title) \
                .order_by(desc('revenue')) \
                .limit(limit).all()

            return results
        finally:
            session.close()

    def get_top_products(self, limit=5):
        """Top sản phẩm bán chạy nhất (theo số lượng)"""
        session = db.get_session()
        try:
            # Join: TicketProduct -> Product
            # Lưu ý: TicketProduct liên kết với Ticket, cần filter Ticket chưa hủy
            results = session.query(
                Product.name,
                func.sum(TicketProduct.quantity).label('qty')
            ).join(Ticket, TicketProduct.ticket_id == Ticket.ticket_id) \
                .join(Product, TicketProduct.product_id == Product.product_id) \
                .filter(Ticket.status != 'cancelled') \
                .group_by(Product.name) \
                .order_by(desc('qty')) \
                .limit(limit).all()

            return results
        finally:
            session.close()