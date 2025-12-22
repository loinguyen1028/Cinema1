import requests

# Thay Key bạn vừa nhận được qua email vào đây
API_KEY = "e009b297"


def fetch_movie_info(movie_name):
    """
    Tìm phim bằng OMDb API (Dữ liệu Tiếng Anh)
    """
    try:
        url = "http://www.omdbapi.com/"
        params = {
            "apikey": API_KEY,
            "t": movie_name  # 't' là tìm kiếm chính xác theo tiêu đề
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        # OMDb trả về 'Response': 'False' nếu không tìm thấy
        if data.get('Response') == 'False':
            return None

        # Xử lý thời lượng (OMDb trả về dạng "162 min") -> Lấy số 162
        runtime_str = data.get('Runtime', '0 min')
        duration = ''.join(filter(str.isdigit, runtime_str))

        return {
            "title": data.get('Title'),
            "actors": data.get('Actors'),  # Tên diễn viên (Tiếng Anh không dấu vẫn chuẩn)
            "genre": data.get('Genre'),  # Ví dụ: Action, Adventure
            "duration": int(duration) if duration else 0,
            "overview": data.get('Plot')  # Tóm tắt (Tiếng Anh)
        }

    except Exception as e:
        print(f"Lỗi OMDb: {e}")
        return None