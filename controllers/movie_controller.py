from services.movie_service import MovieService


class MovieController:
    def __init__(self):
        self.service = MovieService()

    def get_all(self):
        return self.service.get_all_movies()

    def search(self, keyword):
        return self.service.search_movies(keyword)

    def get_detail(self, movie_id):
        return self.service.get_movie_by_id(movie_id)

    def delete(self, movie_id):

        return self.service.delete_movie(movie_id)

    def save(self, mode, movie_id, name, duration, country, genre, actors, lang, age, desc, poster):

        return self.service.save_movie(mode, movie_id, name, duration, country, genre, actors, lang, age, desc, poster)