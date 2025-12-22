import os
import sys
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
import textwrap
from reportlab.pdfgen import canvas

def print_ticket_pdf(data):
    # --- CẤU HÌNH ĐƯỜNG DẪN LƯU FILE ---
    # 1. Định nghĩa thư mục mong muốn (Ổ D)
    drive_path = "D:/"
    folder_name = "Ve_Xem_Phim"

    # Kiểm tra xem máy có ổ D không?
    if os.path.exists(drive_path):
        save_dir = os.path.join(drive_path, folder_name)  # D:\Ve_Xem_Phim
    else:
        # Nếu không có ổ D, lưu tại thư mục hiện tại của dự án
        save_dir = os.path.join(os.getcwd(), folder_name)

    # 2. Tạo thư mục nếu chưa tồn tại (tránh lỗi FileNotFoundError)
    os.makedirs(save_dir, exist_ok=True)

    # 3. Đặt tên file theo Mã vé để không bị trùng đè
    ticket_id = str(data.get('ticket_id', 'unknown'))
    file_name = f"Ticket_{ticket_id}.pdf"
    full_path = os.path.join(save_dir, file_name)

    # --- BẮT ĐẦU VẼ PDF ---
    page_width = 80 * mm
    page_height = 200 * mm
    c = canvas.Canvas(full_path, pagesize=(page_width, page_height))

    # Đăng ký font (như cũ)
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        font_main = 'Arial'
        font_bold = 'Arial'
    except:
        font_main = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    # --- VẼ NỘI DUNG (GIỮ NGUYÊN CODE CŨ) ---
    y = page_height - 10 * mm
    c.setFont(font_bold, 14)
    c.drawCentredString(page_width / 2, y, "LHQ CINEMAS")

    y -= 8 * mm
    c.setFont(font_main, 10)
    c.drawCentredString(page_width / 2, y, "--- VE XEM PHIM ---")

    y -= 10 * mm
    c.setFont(font_bold, 14)
    movie_name = data.get('movie_name', '')
    if len(movie_name) > 20: c.setFont(font_bold, 11)
    c.drawCentredString(page_width / 2, y, movie_name)

    y -= 6 * mm
    c.setFont(font_main, 9)
    # IN FORMAT VÀ PHÒNG CÙNG 1 DÒNG (Dòng này ít khi bị tràn)
    c.drawString(5 * mm, y, f"Format: {data.get('format', '2D')}")
    c.setFont(font_bold, 12)
    c.drawRightString(page_width - 5 * mm, y, f"Phong: {data.get('room', '')}")

    # --- XỬ LÝ IN GHẾ (TỰ ĐỘNG XUỐNG DÒNG) ---
    y -= 10 * mm
    seat_string = f"Ghe: {data.get('seat', '')}"

    c.setFont(font_bold, 16)  # Font to cho rõ

    # Sử dụng textwrap để cắt chuỗi nếu quá dài
    # width=22: Ước lượng khoảng 22 ký tự sẽ vừa chiều ngang tờ vé 80mm với font size 16
    # Bạn có thể tăng giảm số 22 này tùy vào font chữ thực tế
    wrapped_lines = textwrap.wrap(seat_string, width=22)

    for line in wrapped_lines:
        c.drawString(5 * mm, y, line)
        y -= 7 * mm  # Mỗi dòng ghế cách nhau 7mm

    # --- CÁC PHẦN DƯỚI (NGÀY, GIỜ...) ---
    # Lưu ý: Vì số dòng ghế thay đổi, biến y đã tự động giảm xuống
    # nên các phần dưới sẽ tự động được đẩy xuống theo, không bị đè.

    y -= 5 * mm  # Khoảng cách đệm thêm trước khi in Ngày
    c.setFont(font_main, 10)
    c.drawString(5 * mm, y, f"Ngay: {data.get('date', '')}")

    y -= 5 * mm
    c.drawString(5 * mm, y, f"Suat: {data.get('time', '')}")

    y -= 10 * mm
    c.setDash(1, 2)
    c.line(5 * mm, y, page_width - 5 * mm, y)
    y -= 8 * mm
    c.setDash([])

    c.setFont(font_bold, 12)
    c.drawString(5 * mm, y, "TONG CONG:")
    c.drawRightString(page_width - 5 * mm, y, f"{data.get('price', 0):,} VND")

    # --- FOOTER INFO (Sửa đoạn này) ---
    y -= 12 * mm
    c.setFont(font_main, 9)
    # Hiển thị tên nhân viên
    c.drawString(5 * mm, y, f"Seller: {data.get('seller', 'Admin')}")

    # Hiển thị giờ in vé (Hiện tại)
    from datetime import datetime
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.drawRightString(page_width - 5 * mm, y, current_time)

    # --- BARCODE (ĐÃ SỬA LỖI renderScale) ---
    y -= 15 * mm
    barcode = code128.Code128(ticket_id, barHeight=12 * mm, barWidth=1.2)
    barcode.drawOn(c, 10 * mm, y)  # <--- Dùng drawOn thay vì renderPDF.draw

    y -= 5 * mm
    c.setFont(font_main, 9)
    c.drawCentredString(page_width / 2, y, ticket_id)

    y -= 5 * mm
    c.setFont(font_main, 8)
    c.drawCentredString(page_width / 2, y, "Cam on quy khach!")

    # Lưu file
    c.save()
    print(f"Đã lưu vé tại: {full_path}")

    # Tự động mở file từ đường dẫn mới
    if sys.platform == "win32":
        os.startfile(full_path)
    else:
        subprocess.call(["open", full_path])