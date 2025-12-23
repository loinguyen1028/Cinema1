import os
import sys
import subprocess
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128


def print_ticket_pdf(data):
    # --- CẤU HÌNH ---
    drive_path = "D:/"
    folder_name = "Ve_Xem_Phim"
    save_dir = os.path.join(drive_path, folder_name) if os.path.exists(drive_path) else os.path.join(os.getcwd(),
                                                                                                     folder_name)
    os.makedirs(save_dir, exist_ok=True)

    # Đặt tên file có timestamp để không bị lỗi đè file
    import time
    timestamp = int(time.time())
    ticket_id = str(data.get('ticket_id', 'unknown'))
    file_name = f"Bill_{ticket_id}_{timestamp}.pdf"
    full_path = os.path.join(save_dir, file_name)

    # KIỂM TRA LOẠI VÉ: Có tên phim hay không?
    is_movie_ticket = bool(data.get('movie_name'))

    # Tính chiều dài giấy
    # Nếu là vé phim có bắp nước -> dài 250mm, không bắp -> 180mm
    # Nếu là hóa đơn bán lẻ -> Dài tùy thuộc số lượng món (tối thiểu 150mm)
    if is_movie_ticket:
        page_height = 250 * mm if data.get('food') else 180 * mm
    else:
        # Hóa đơn bán lẻ: Tự động dài ra nếu mua nhiều món
        food_count = len(data.get('food', '').split(', '))
        page_height = (120 + food_count * 10) * mm

    page_width = 80 * mm
    c = canvas.Canvas(full_path, pagesize=(page_width, page_height))

    # Font
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        font_main = 'Arial'
        font_bold = 'Arial'
    except:
        font_main = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    # =========================================================
    # TRƯỜNG HỢP 1: VÉ XEM PHIM (GIỮ NGUYÊN CODE CŨ CỦA BẠN)
    # =========================================================
    if is_movie_ticket:
        # ... (Phần code in vé phim + phiếu cắt rời -> Bạn giữ nguyên như cũ) ...
        # Để code gọn, mình chỉ tóm tắt lại cấu trúc, bạn paste lại đoạn code cũ vào đây
        # Hoặc dùng đoạn code đầy đủ bên dưới nếu muốn đồng bộ
        draw_movie_ticket(c, data, page_width, page_height, font_main, font_bold)

    # =========================================================
    # TRƯỜNG HỢP 2: HÓA ĐƠN BÁN LẺ (CHO KHÁCH MUA BẮP NƯỚC)
    # =========================================================
    else:
        y = page_height - 10 * mm
        c.setFont(font_bold, 14)
        c.drawCentredString(page_width / 2, y, "LHQ CINEMAS")

        y -= 6 * mm
        c.setFont(font_main, 10)
        c.drawCentredString(page_width / 2, y, "--- HOA DON BAN LE ---")

        y -= 8 * mm
        c.setFont(font_main, 9)
        c.drawString(5 * mm, y, f"Ngay: {data.get('date')} {data.get('time')}")

        y -= 5 * mm
        c.drawString(5 * mm, y, f"Thu ngan: {data.get('seller', 'Staff')}")

        y -= 5 * mm
        c.drawString(5 * mm, y, f"Ma HD: {ticket_id}")

        # Kẻ dòng
        y -= 5 * mm
        c.setDash(1, 2)
        c.line(5 * mm, y, page_width - 5 * mm, y)
        c.setDash([])

        # Danh sách món
        y -= 8 * mm
        c.setFont(font_bold, 10)
        c.drawString(5 * mm, y, "San pham")
        c.drawRightString(page_width - 5 * mm, y, "Thanh tien")

        y -= 6 * mm
        c.setFont(font_main, 10)

        food_list = data.get('food', '').split(', ')
        # Food string dạng: "2x Bắp, 1x Nước" -> Cần tách giá tiền nếu muốn chi tiết
        # Nhưng ở đây ta in danh sách món, giá tổng ở dưới

        for item in food_list:
            # item ví dụ: "2x Bắp Ngọt"
            wrapped = textwrap.wrap(item, width=35)
            for line in wrapped:
                c.drawString(5 * mm, y, line)
                y -= 5 * mm

        # Kẻ dòng tổng
        y -= 5 * mm
        c.line(5 * mm, y, page_width - 5 * mm, y)

        y -= 8 * mm
        c.setFont(font_bold, 14)
        c.drawString(5 * mm, y, "TONG:")
        c.drawRightString(page_width - 5 * mm, y, f"{data.get('price', 0):,} d")

        # Barcode
        y -= 20 * mm
        try:
            barcode = code128.Code128(ticket_id, barHeight=10 * mm, barWidth=1.2)
            barcode.drawOn(c, 10 * mm, y)
        except:
            pass

        y -= 5 * mm
        c.setFont(font_main, 8)
        c.drawCentredString(page_width / 2, y, "Cam on quy khach!")

    c.save()
    if sys.platform == "win32":
        try:
            os.startfile(full_path)
        except:
            pass


# Hàm phụ trợ vẽ vé phim (Tách ra từ code cũ cho gọn)
def draw_movie_ticket(c, data, w, h, font_main, font_bold):
    y = h - 10 * mm
    c.setFont(font_bold, 14)
    c.drawCentredString(w / 2, y, "LHQ CINEMAS")
    y -= 6 * mm
    c.setFont(font_main, 9)
    c.drawCentredString(w / 2, y, "--- VE XEM PHIM ---")

    y -= 10 * mm
    c.setFont(font_bold, 14)
    movie_name = data.get('movie_name', '')
    for line in textwrap.wrap(movie_name, width=20):
        c.drawCentredString(w / 2, y, line)
        y -= 6 * mm

    y -= 2 * mm
    c.setFont(font_main, 10)
    c.drawString(5 * mm, y, f"Format: {data.get('format', '2D')}")
    c.setFont(font_bold, 12)
    c.drawRightString(w - 5 * mm, y, f"R: {data.get('room', '')}")

    y -= 10 * mm
    seat_string = f"Ghe/Seat: {data.get('seat', '')}"
    c.setFont(font_bold, 18)
    for line in textwrap.wrap(seat_string, width=20):
        c.drawString(5 * mm, y, line)
        y -= 7 * mm

    y -= 5 * mm
    c.setFont(font_main, 10)
    c.drawString(5 * mm, y, f"Ngay: {data.get('date', '')}")
    y -= 5 * mm
    c.drawString(5 * mm, y, f"Suat: {data.get('time', '')}")

    y -= 10 * mm
    c.setFont(font_bold, 12)
    c.drawRightString(w - 5 * mm, y, f"{data.get('price', 0):,} VND")

    y -= 15 * mm
    try:
        barcode = code128.Code128(str(data.get('ticket_id')), barHeight=10 * mm, barWidth=1.2)
        barcode.drawOn(c, 10 * mm, y)
    except:
        pass

    y -= 4 * mm
    c.setFont(font_main, 8)
    c.drawCentredString(w / 2, y, str(data.get('ticket_id')))

    # PHIẾU BẮP NƯỚC CẮT RỜI
    if data.get('food'):
        y -= 10 * mm
        c.setDash(3, 3)
        c.line(2 * mm, y, w - 2 * mm, y)
        c.setDash([])
        c.drawCentredString(w / 2, y - 3 * mm, "✂ --- Cắt tại đây --- ✂")

        y -= 12 * mm
        c.setFont(font_bold, 14)
        c.drawCentredString(w / 2, y, "PHIEU BAP NUOC")
        y -= 6 * mm
        c.setFont(font_main, 9)
        c.drawCentredString(w / 2, y, "(Dua phieu nay tai quay Cantin)")

        y -= 10 * mm
        c.setFont(font_bold, 11)
        food_list = data.get('food', '').split(', ')
        for item in food_list:
            wrapped = textwrap.wrap(item.strip(), width=28)
            if wrapped:
                c.drawString(5 * mm, y, f"• {wrapped[0]}")
                y -= 5 * mm
            for line in wrapped[1:]:
                c.drawString(9 * mm, y, line)
                y -= 5 * mm

        y -= 5 * mm
        c.setFont(font_main, 8)
        c.drawString(5 * mm, y, f"Ref: {data.get('ticket_id')}")

    y -= 10 * mm
    c.drawCentredString(w / 2, y, "Cam on quy khach!")