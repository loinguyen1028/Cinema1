import requests

MY_KEY = "DÁN_KEY_CỦA_BẠN_VÀO_ĐÂY"


def test_connection():
    print(f"--- Đang test với Key: {MY_KEY} ---")

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": MY_KEY,
        "t": "Titanic"
    }

    try:
        resp = requests.get(url, params=params)
        data = resp.json()

        print("Kết quả trả về từ Server:")
        print(data)

        if data.get('Response') == 'True':
            print("\n✅ THÀNH CÔNG! API hoạt động tốt.")
        else:
            print("\n❌ THẤT BẠI! Lỗi do: " + data.get('Error', 'Không rõ'))

    except Exception as e:
        print("\n❌ LỖI CODE/MẠNG: ", e)


test_connection()