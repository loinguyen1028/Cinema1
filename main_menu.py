# main_menu.py
import tkinter as tk
from tkinter import messagebox
from datetime import date
import os

from customers_window import CustomersWindow
from booking_window import BookingWindow
from admin_movies_window import AdminMoviesWindow
from db import get_connection

from PIL import Image, ImageTk  # pip install pillow


class MainMenu:
    def __init__(self, root, user_id, full_name, role_name, on_logout):
        self.root = root
        self.user_id = user_id
        self.full_name = full_name
        self.role_name = role_name
        self.on_logout = on_logout

        self.root.title("Quản lý rạp chiếu phim")
        self.root.geometry("1200x700")

        # giữ reference ảnh để không bị GC
        self.poster_imgs_now = []
        self.poster_imgs_soon = []

        # ========== THANH MENU TRÊN ==========
        top_frame = tk.Frame(root, bg="#ff8800", height=60)
        top_frame.pack(fill=tk.X)

        buttons = [
            ("Tìm Khách", self.btn_find_customer),
            ("Khách Hàng", self.btn_customers),
            ("Đặt vé điện thoại", self.btn_booking),
            ("Hóa Đơn Mới", self.btn_booking),
            ("Phim Đang Chiếu", self.btn_booking),
            ("Phim Sắp Chiếu", self.btn_booking),
            ("Combo", self.btn_combo),
            ("Vé Online", self.btn_online_ticket),
            ("Thoát", self.logout)
        ]

        for text, cmd in buttons:
            b = tk.Button(top_frame, text=text, command=cmd,
                          bg="#ffa726", fg="black", padx=10, pady=5)
            b.pack(side=tk.LEFT, padx=3, pady=5)

        lbl_user = tk.Label(top_frame,
                            text=f"User: {full_name} ({role_name})",
                            bg="#ff8800", fg="white")
        lbl_user.pack(side=tk.RIGHT, padx=10)

        if role_name == "ADMIN":
            admin_btn = tk.Button(top_frame, text="Admin: Phim & Suất chiếu",
                                  command=self.btn_admin_movies,
                                  bg="#ff7043", fg="white")
            admin_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # ========== VÙNG MAIN ==========
        main_frame = tk.Frame(root, bg="#333333")
        main_frame.pack(fill=tk.BOTH, expand=True)


        # Trung tâm: chỉ còn 2 hàng poster
        center = tk.Frame(main_frame, bg="#444444")
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.build_poster_area(center)
        self.load_schedule_movies()

    # ========== GIAO DIỆN 2 HÀNG POSTER ==========
    def build_poster_area(self, parent):
        title = tk.Label(parent, text="Lịch chiếu phim",
                         bg="#444444", fg="white",
                         font=("Arial", 14, "bold"))
        title.pack(pady=5)

        # Hàng poster phim đang chiếu
        lbl_now_post = tk.Label(parent, text="Phim đang chiếu (hôm nay)",
                                bg="#444444", fg="white",
                                font=("Arial", 12, "bold"))
        lbl_now_post.pack(anchor="w", padx=5, pady=(10, 0))

        self.row_now_posters = tk.Frame(parent, bg="#444444")
        self.row_now_posters.pack(fill=tk.X, padx=5, pady=(0, 10))

        # Hàng poster phim sắp chiếu
        lbl_soon_post = tk.Label(parent, text="Phim sắp chiếu (sau hôm nay)",
                                 bg="#444444", fg="white",
                                 font=("Arial", 12, "bold"))
        lbl_soon_post.pack(anchor="w", padx=5, pady=(10, 0))

        self.row_soon_posters = tk.Frame(parent, bg="#444444")
        self.row_soon_posters.pack(fill=tk.X, padx=5, pady=(0, 10))

    def load_schedule_movies(self):
        """Lấy phim đang chiếu & sắp chiếu, hiển thị thành poster card."""
        today = date.today()

        # clear poster cũ
        for w in self.row_now_posters.winfo_children():
            w.destroy()
        for w in self.row_soon_posters.winfo_children():
            w.destroy()
        self.poster_imgs_now.clear()
        self.poster_imgs_soon.clear()

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Phim đang chiếu (có suất chiếu trong ngày hôm nay)
            cur.execute("""
                SELECT m.movie_id,
                       m.title,
                       MIN(s.start_time) AS first_time,
                       m.poster_path
                FROM movies m
                JOIN showtimes s ON m.movie_id = s.movie_id
                WHERE s.start_time::date = %s
                GROUP BY m.movie_id, m.title, m.poster_path
                ORDER BY first_time
            """, (today,))
            rows_now = cur.fetchall()

            # Phim sắp chiếu (suất chiếu sau hôm nay)
            cur.execute("""
                SELECT m.movie_id,
                       m.title,
                       MIN(s.start_time) AS first_time,
                       m.poster_path
                FROM movies m
                JOIN showtimes s ON m.movie_id = s.movie_id
                WHERE s.start_time::date > %s
                GROUP BY m.movie_id, m.title, m.poster_path
                ORDER BY first_time
            """, (today,))
            rows_soon = cur.fetchall()

            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return

        # tạo card poster
        for mid, title, first_time, poster in rows_now:
            self.add_poster_card(self.row_now_posters,
                                 mid, title, first_time, poster, "now")

        for mid, title, first_time, poster in rows_soon:
            self.add_poster_card(self.row_soon_posters,
                                 mid, title, first_time, poster, "soon")

    def add_poster_card(self, parent, movie_id, title, first_time, poster_path, group):
        """
        Card gồm:
        [ẢNH]
        [TÊN PHIM]
        [GIỜ CHIẾU ĐẦU TIÊN]
        """
        card = tk.Frame(parent, bg="#222222", bd=1, relief=tk.RIDGE)
        card.pack(side=tk.LEFT, padx=5, pady=5)

        img_label = tk.Label(card, bg="#222222")
        img_label.pack(padx=3, pady=3)

        # load ảnh
        photo = None
        if poster_path:
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                img_path = os.path.join(base_dir, poster_path)
                if os.path.exists(img_path):
                    from PIL import Image
                    img = Image.open(img_path)
                    img = img.resize((150, 220), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label.config(image=photo)
            except Exception as e:
                print("Lỗi load ảnh poster:", e)

        if photo is None:
            img_label.config(text="No Image", fg="white")

        if photo is not None:
            if group == "now":
                self.poster_imgs_now.append(photo)
            else:
                self.poster_imgs_soon.append(photo)

        # label tiêu đề phim
        title_label = tk.Label(card, text=title,
                               bg="#ff6600", fg="white",
                               wraplength=150, justify="center")
        title_label.pack(fill=tk.X)

        # label thời gian (giờ + ngày)
        time_str = ""
        if first_time:
            try:
                # first_time là kiểu timestamp, format lại
                time_str = first_time.strftime("%H:%M %d/%m/%Y")
            except Exception:
                time_str = str(first_time)

        time_label = tk.Label(card, text=time_str,
                              bg="#333333", fg="white",
                              wraplength=150, justify="center")
        time_label.pack(fill=tk.X, pady=(0, 3))

        # click vào card / ảnh / chữ -> mở đặt vé
        def open_booking(event=None):
            self.btn_booking()

        card.bind("<Button-1>", open_booking)
        img_label.bind("<Button-1>", open_booking)
        title_label.bind("<Button-1>", open_booking)
        time_label.bind("<Button-1>", open_booking)

    # ========== CÁC CHỨC NĂNG MENU ==========
    def btn_find_customer(self):
        top = tk.Toplevel(self.root)
        top.title("Tìm khách hàng")

        tk.Label(top, text="Nhập SĐT:").pack(padx=5, pady=5)
        entry = tk.Entry(top)
        entry.pack(padx=5, pady=5)

        def do_search():
            phone = entry.get().strip()
            if not phone:
                messagebox.showwarning("Thiếu dữ liệu", "Nhập số điện thoại")
                return
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT name, email
                    FROM customers
                    WHERE phone=%s
                """, (phone,))
                row = cur.fetchone()
                conn.close()
            except Exception as e:
                messagebox.showerror("Lỗi DB", str(e))
                return

            if row:
                name, email = row
                messagebox.showinfo("Kết quả",
                                    f"Tên: {name}\nEmail: {email}")
            else:
                messagebox.showinfo("Kết quả",
                                    "Không tìm thấy khách này")

        tk.Button(top, text="Tìm", command=do_search).pack(padx=5, pady=5)

    def btn_customers(self):
        CustomersWindow(self.root)

    def btn_booking(self):
        BookingWindow(self.root, self.user_id)

    def btn_combo(self):
        messagebox.showinfo("Combo",
                            "Demo: chức năng bán combo có thể gắn thêm bảng combos riêng.")

    def btn_online_ticket(self):
        messagebox.showinfo("Vé Online",
                            "Demo: có thể đồng bộ với hệ thống vé online sau.")

    def btn_admin_movies(self):
        AdminMoviesWindow(self.root)
        # sau khi admin thêm suất chiếu / phim mới, load lại poster
        self.load_schedule_movies()

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            self.on_logout()
