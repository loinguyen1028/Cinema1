import requests

API_KEY = "e009b297"


def fetch_movie_info(movie_name):
    try:
        url = "http://www.omdbapi.com/"
        params = {
            "apikey": API_KEY,
            "t": movie_name
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        if data.get("Response") == "False":
            return None

        runtime_str = data.get("Runtime", "0 min")
        duration = "".join(filter(str.isdigit, runtime_str))

        return {
            "title": data.get("Title"),
            "actors": data.get("Actors"),
            "genre": data.get("Genre"),
            "duration": int(duration) if duration else 0,
            "overview": data.get("Plot")
        }

    except Exception as e:
        print(f"Lỗi OMDb: {e}")
        return None
