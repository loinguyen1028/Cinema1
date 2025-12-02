# admin_movies_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_connection
import os
import shutil


class AdminMoviesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Quản lý phim & suất chiếu (Admin)")
        self.geometry("950x520")

        # Đường dẫn file ảnh gốc mà admin chọn
        self.poster_source_path = None

        # --- Form phim ---
        form = tk.LabelFrame(self, text="Phim")
        form.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(form, text="Tiêu đề:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        tk.Label(form, text="Thời lượng (phút):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Label(form, text="Ảnh poster:").grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.var_movie_id = None
        self.entry_title = tk.Entry(form, width=40)
        self.entry_duration = tk.Entry(form, width=10)
        self.entry_poster = tk.Entry(form, width=40, state="readonly")  # chỉ hiển thị tên file

        self.entry_title.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.entry_duration.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.entry_poster.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        btn_choose_poster = tk.Button(form, text="Chọn ảnh...",
                                      command=self.choose_poster)
        btn_choose_poster.grid(row=2, column=2, padx=5, pady=2)

        btn_frame = tk.Frame(form)
        btn_frame.grid(row=0, column=3, rowspan=3, padx=10)

        tk.Button(btn_frame, text="Thêm", command=self.add_movie).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Cập nhật", command=self.update_movie).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Xóa", command=self.delete_movie).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Làm mới", command=self.clear_form).pack(fill=tk.X, pady=2)

        # --- Bảng phim ---
        self.tree_movies = ttk.Treeview(self,
                                        columns=("id", "title", "dur", "poster"),
                                        show="headings", height=6)
        self.tree_movies.heading("id", text="ID")
        self.tree_movies.heading("title", text="Tiêu đề")
        self.tree_movies.heading("dur", text="Phút")
        self.tree_movies.heading("poster", text="Poster")
        self.tree_movies.column("id", width=50)
        self.tree_movies.column("poster", width=200)
        self.tree_movies.pack(fill=tk.X, padx=5, pady=5)
        self.tree_movies.bind("<<TreeviewSelect>>", self.on_movie_select)

        # --- Khối suất chiếu ---
        show_frame = tk.LabelFrame(self, text="Suất chiếu cho phim đã chọn")
        show_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(show_frame, text="Phòng:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        tk.Label(show_frame, text="Thời gian (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Label(show_frame, text="Giá vé:").grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.cbo_room = ttk.Combobox(show_frame, state="readonly")
        self.cbo_room.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.entry_time = tk.Entry(show_frame, width=20)
        self.entry_time.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.entry_price = tk.Entry(show_frame, width=10)
        self.entry_price.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        tk.Button(show_frame, text="Thêm suất chiếu",
                  command=self.add_showtime).grid(row=0, column=2, rowspan=3, padx=10)

        self.tree_showtimes = ttk.Treeview(show_frame,
                                           columns=("id", "time", "room", "price"),
                                           show="headings", height=6)
        self.tree_showtimes.heading("id", text="ID")
        self.tree_showtimes.heading("time", text="Thời gian")
        self.tree_showtimes.heading("room", text="Phòng")
        self.tree_showtimes.heading("price", text="Giá")
        self.tree_showtimes.column("id", width=50)
        self.tree_showtimes.grid(row=3, column=0, columnspan=3,
                                 sticky="nsew", padx=5, pady=5)

        show_frame.rowconfigure(3, weight=1)
        show_frame.columnconfigure(1, weight=1)

        self.load_rooms()
        self.load_movies()

    # ============= CHỌN ẢNH POSTER =============
    def choose_poster(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh poster",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")]
        )
        if not path:
            return
        self.poster_source_path = path
        # Chỉ hiển thị tên file trong ô
        filename = os.path.basename(path)
        self.entry_poster.config(state="normal")
        self.entry_poster.delete(0, tk.END)
        self.entry_poster.insert(0, filename)
        self.entry_poster.config(state="readonly")

    # ============= LOAD DỮ LIỆU =============
    def load_rooms(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT room_id, room_name FROM rooms ORDER BY room_name")
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            return
        self.room_map = {f"{name} (ID {rid})": rid for rid, name in rows}
        self.cbo_room["values"] = list(self.room_map.keys())

    def load_movies(self):
        for i in self.tree_movies.get_children():
            self.tree_movies.delete(i)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT movie_id, title, duration_min, poster_path FROM movies ORDER BY movie_id")
            for mid, title, dur, poster in cur.fetchall():
                self.tree_movies.insert("", tk.END, values=(mid, title, dur, poster or ""))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # ============= XỬ LÝ FORM PHIM =============
    def clear_form(self):
        self.var_movie_id = None
        self.poster_source_path = None
        self.entry_title.delete(0, tk.END)
        self.entry_duration.delete(0, tk.END)
        self.entry_poster.config(state="normal")
        self.entry_poster.delete(0, tk.END)
        self.entry_poster.config(state="readonly")

    def on_movie_select(self, event=None):
        selected = self.tree_movies.selection()
        if not selected:
            return
        mid, title, dur, poster = self.tree_movies.item(selected[0])["values"]
        self.var_movie_id = mid
        self.poster_source_path = None   # khi chọn từ list, chưa chọn ảnh mới

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, title)

        self.entry_duration.delete(0, tk.END)
        self.entry_duration.insert(0, dur)

        self.entry_poster.config(state="normal")
        self.entry_poster.delete(0, tk.END)
        if poster:
            self.entry_poster.insert(0, os.path.basename(poster))
        self.entry_poster.config(state="readonly")

        self.load_showtimes(mid)

    def add_movie(self):
        title = self.entry_title.get().strip()
        dur = self.entry_duration.get().strip()
        if not title or not dur:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập tiêu đề và thời lượng")
            return
        try:
            dur_int = int(dur)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Thời lượng phải là số nguyên")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            # B1: thêm phim, chưa có poster_path, lấy ra movie_id
            cur.execute("""
                INSERT INTO movies (title, duration_min)
                VALUES (%s, %s)
                RETURNING movie_id
            """, (title, dur_int))
            movie_id = cur.fetchone()[0]

            poster_rel_path = None
            # B2: nếu admin có chọn ảnh, copy vào thư mục posters và cập nhật đường dẫn
            if self.poster_source_path:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                posters_dir = os.path.join(base_dir, "posters")
                os.makedirs(posters_dir, exist_ok=True)

                ext = os.path.splitext(self.poster_source_path)[1]  # .jpg / .png...
                poster_filename = f"movie_{movie_id}{ext}"
                poster_rel_path = os.path.join("posters", poster_filename)
                poster_dest = os.path.join(base_dir, poster_rel_path)

                shutil.copy2(self.poster_source_path, poster_dest)

                cur.execute("""
                    UPDATE movies
                    SET poster_path = %s
                    WHERE movie_id = %s
                """, (poster_rel_path, movie_id))

            conn.commit()
            conn.close()
            self.clear_form()
            self.load_movies()
            msg = "Đã thêm phim"
            if poster_rel_path:
                msg += f"\nPoster: {poster_rel_path}"
            messagebox.showinfo("Thành công", msg)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def update_movie(self):
        if not self.var_movie_id:
            messagebox.showwarning("Chọn phim", "Chọn một phim để cập nhật")
            return

        title = self.entry_title.get().strip()
        dur = self.entry_duration.get().strip()
        if not title or not dur:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập tiêu đề và thời lượng")
            return
        try:
            dur_int = int(dur)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Thời lượng phải là số nguyên")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Cập nhật tiêu đề + thời lượng
            cur.execute("""
                UPDATE movies
                SET title=%s, duration_min=%s
                WHERE movie_id=%s
            """, (title, dur_int, self.var_movie_id))

            # Nếu admin vừa chọn ảnh mới -> copy & cập nhật poster_path
            if self.poster_source_path:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                posters_dir = os.path.join(base_dir, "posters")
                os.makedirs(posters_dir, exist_ok=True)

                ext = os.path.splitext(self.poster_source_path)[1]
                poster_filename = f"movie_{self.var_movie_id}{ext}"
                poster_rel_path = os.path.join("posters", poster_filename)
                poster_dest = os.path.join(base_dir, poster_rel_path)

                shutil.copy2(self.poster_source_path, poster_dest)

                cur.execute("""
                    UPDATE movies
                    SET poster_path = %s
                    WHERE movie_id = %s
                """, (poster_rel_path, self.var_movie_id))

            conn.commit()
            conn.close()
            self.load_movies()
            messagebox.showinfo("Thành công", "Đã cập nhật phim")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def delete_movie(self):
        if not self.var_movie_id:
            messagebox.showwarning("Chọn phim", "Chọn một phim để xóa")
            return
        if not messagebox.askyesno("Xác nhận",
                                   "Xóa phim này (sẽ xóa cả suất chiếu liên quan)?"):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM movies WHERE movie_id=%s",
                        (self.var_movie_id,))
            conn.commit()
            conn.close()
            self.var_movie_id = None
            self.clear_form()
            self.load_movies()
            for i in self.tree_showtimes.get_children():
                self.tree_showtimes.delete(i)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # ============= SUẤT CHIẾU =============
    def load_showtimes(self, movie_id):
        for i in self.tree_showtimes.get_children():
            self.tree_showtimes.delete(i)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT s.showtime_id, s.start_time, r.room_name, s.ticket_price
                FROM showtimes s
                JOIN rooms r ON s.room_id = r.room_id
                WHERE s.movie_id=%s
                ORDER BY s.start_time
            """, (movie_id,))
            for sid, stime, rname, price in cur.fetchall():
                self.tree_showtimes.insert("", tk.END,
                                           values=(sid, stime, rname, price))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def add_showtime(self):
        if not self.var_movie_id:
            messagebox.showwarning("Chọn phim", "Chọn phim trước")
            return
        room_key = self.cbo_room.get()
        if not room_key:
            messagebox.showwarning("Thiếu dữ liệu", "Chọn phòng")
            return
        room_id = self.room_map[room_key]
        time_str = self.entry_time.get().strip()
        price = self.entry_price.get().strip()
        if not time_str or not price:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập thời gian & giá vé")
            return
        try:
            price_val = float(price)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Giá vé phải là số")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO showtimes (movie_id, room_id, start_time, ticket_price)
                VALUES (%s, %s, %s, %s)
            """, (self.var_movie_id, room_id, time_str, price_val))
            conn.commit()
            conn.close()
            self.load_showtimes(self.var_movie_id)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
