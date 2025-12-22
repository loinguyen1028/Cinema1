from sqlalchemy import func, desc, extract, cast, Date
from db import db
# Đảm bảo imports đúng các model của bạn
from models import Ticket, TicketProduct, TicketSeat, Product, Movie, Showtime, Room, Customer, Seat


class StatsDAO:
    # --- NHÓM 1: TÀI CHÍNH ---
    def get_revenue_by_date_range(self, start_date, end_date):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            results = session.query(date_col, func.sum(Ticket.total_amount)) \
                .filter(date_col >= start_date, date_col <= end_date) \
                .group_by(date_col).all()
            return results
        except Exception as e:
            print(f"Lỗi Revenue: {e}")
            return []
        finally:
            session.close()

    # 2. Cơ cấu doanh thu (Vé vs Bắp nước)
    def get_revenue_structure(self, start_date, end_date):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            ticket_rev = session.query(func.sum(TicketSeat.price)) \
                             .join(Ticket).filter(date_col >= start_date, date_col <= end_date).scalar() or 0

            product_rev = session.query(func.sum(TicketProduct.quantity * TicketProduct.price_at_purchase)) \
                              .join(Ticket).filter(date_col >= start_date, date_col <= end_date).scalar() or 0

            return ticket_rev, product_rev
        except Exception as e:
            print(f"Lỗi Structure: {e}")
            return 0, 0
        finally:
            session.close()

    # 3. Doanh thu theo Phòng chiếu
    def get_revenue_by_room(self, start_date, end_date):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            results = session.query(Room.room_name, func.sum(Ticket.total_amount)) \
                .join(Showtime, Room.room_id == Showtime.room_id) \
                .join(Ticket, Showtime.showtime_id == Ticket.showtime_id) \
                .filter(date_col >= start_date, date_col <= end_date) \
                .group_by(Room.room_name).all()
            return results
        except Exception as e:
            print(f"Lỗi Room Revenue: {e}")
            return []
        finally:
            session.close()

    # --- NHÓM 2: HIỆU SUẤT & SẢN PHẨM ---
    # 4. Top Phim
    def get_top_movies(self, start_date, end_date, limit=5):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            results = session.query(Movie.title, func.count(TicketSeat.seat_id).label('qty'),
                                    func.sum(TicketSeat.price)) \
                .join(Showtime, Movie.movie_id == Showtime.movie_id) \
                .join(Ticket, Showtime.showtime_id == Ticket.showtime_id) \
                .join(TicketSeat, Ticket.ticket_id == TicketSeat.ticket_id) \
                .filter(date_col >= start_date, date_col <= end_date) \
                .group_by(Movie.title).order_by(desc('qty')).limit(limit).all()
            return results
        except Exception as e:
            print(f"Lỗi Top Movies: {e}")
            return []
        finally:
            session.close()

    # 5. Top Sản phẩm
    def get_top_products(self, start_date, end_date, limit=5):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            results = session.query(Product.name, func.sum(TicketProduct.quantity).label('qty')) \
                .join(Ticket, TicketProduct.ticket_id == Ticket.ticket_id) \
                .join(Product, TicketProduct.product_id == Product.product_id) \
                .filter(date_col >= start_date, date_col <= end_date) \
                .group_by(Product.name).order_by(desc('qty')).limit(limit).all()
            return results
        except Exception as e:
            print(f"Lỗi Top Products: {e}")
            return []
        finally:
            session.close()

    # 6. Khung giờ vàng (Fix cho PostgreSQL dùng extract)
    def get_golden_hours(self, start_date, end_date):
        session = db.get_session()
        try:
            # Cần so sánh ngày dựa trên giờ chiếu (Showtime) chứ không phải ngày bán vé
            # Logic: Lấy ra Giờ của suất chiếu (Showtime.start_time)

            # Buộc phải join bảng Ticket -> Showtime
            hour_col = extract('hour', Showtime.start_time)

            # Đếm số vé bán được theo giờ chiếu
            raw_results = session.query(hour_col, func.count(Ticket.ticket_id)) \
                .join(Showtime, Ticket.showtime_id == Showtime.showtime_id) \
                .filter(
                cast(Showtime.start_time, Date) >= start_date,
                cast(Showtime.start_time, Date) <= end_date
            ).group_by(hour_col).all()

            data_map = {int(r[0]): r[1] for r in raw_results}

            final_stats = []

            # SỬA: Chạy full từ 0h đến 23h (range(0, 24)) để bắt được suất 3h sáng
            for h in range(0, 24):
                qty = data_map.get(h, 0)
                final_stats.append((f"{h:02d}h", qty))

            return final_stats
        except Exception as e:
            print(f"Lỗi Golden Hours: {e}")
            return []
        finally:
            session.close()

    # --- NHÓM 3: KHÁCH HÀNG ---

    # 7. Khách Thành viên vs Vãng lai
    def get_customer_type_stats(self, start_date, end_date):
        session = db.get_session()
        try:
            date_col = cast(Ticket.booking_time, Date)

            member_count = session.query(func.count(Ticket.ticket_id)) \
                               .filter(Ticket.customer_id != None, date_col >= start_date,
                                       date_col <= end_date).scalar() or 0

            walkin_count = session.query(func.count(Ticket.ticket_id)) \
                               .filter(Ticket.customer_id == None, date_col >= start_date,
                                       date_col <= end_date).scalar() or 0

            return member_count, walkin_count
        except Exception as e:
            print(f"Lỗi Customer Stats: {e}")
            return 0, 0
        finally:
            session.close()

    # 8. Tỷ lệ lấp đầy theo Phòng (%)
    def get_occupancy_rate(self, start_date, end_date):
        session = db.get_session()
        try:
            # 1. Lấy danh sách các phim có chiếu trong khoảng thời gian này
            movies = session.query(Movie).join(Showtime).filter(
                cast(Showtime.start_time, Date) >= start_date,
                cast(Showtime.start_time, Date) <= end_date
            ).distinct().all()

            stats = []

            for movie in movies:
                # A. TÍNH TỔNG SỨC CHỨA (Total Capacity) CỦA PHIM NÀY
                # Logic: Tìm tất cả suất chiếu của phim -> Cộng tổng số ghế của các phòng chiếu đó lại
                showtimes = session.query(Showtime).filter(
                    Showtime.movie_id == movie.movie_id,
                    cast(Showtime.start_time, Date) >= start_date,
                    cast(Showtime.start_time, Date) <= end_date
                ).all()

                total_capacity = 0
                for show in showtimes:
                    # Đếm số ghế của phòng chiếu tại suất đó
                    room_seats = session.query(func.count(Seat.seat_id)).filter(
                        Seat.room_id == show.room_id).scalar() or 0
                    total_capacity += room_seats

                if total_capacity == 0: continue

                # B. TÍNH TỔNG VÉ ĐÃ BÁN (Sold Tickets) CỦA PHIM NÀY
                sold_count = session.query(func.count(TicketSeat.seat_id)) \
                                 .join(Ticket, TicketSeat.ticket_id == Ticket.ticket_id) \
                                 .join(Showtime, Ticket.showtime_id == Showtime.showtime_id) \
                                 .filter(
                    Showtime.movie_id == movie.movie_id,
                    cast(Showtime.start_time, Date) >= start_date,
                    cast(Showtime.start_time, Date) <= end_date
                ).scalar() or 0

                # C. Tính phần trăm
                rate = (sold_count / total_capacity) * 100
                stats.append((movie.title, round(rate, 2)))  # (Tên phim, %)

            # Sắp xếp phim có tỷ lệ lấp đầy từ cao xuống thấp
            stats.sort(key=lambda x: x[1], reverse=True)
            return stats

        except Exception as e:
            print(f"Lỗi Occupancy: {e}")
            return []
        finally:
            session.close()