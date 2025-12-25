from services.showtime_service import ShowtimeService


class ShowtimeController:
    def __init__(self):
        self.service = ShowtimeService()

    def get_list(self, date_filter=None, room_filter=None):
        return self.service.get_list(date_filter, room_filter)

    def get_detail(self, st_id):
        return self.service.get_detail(st_id)

    def get_resources(self):

        from services.movie_service import MovieService
        from services.room_service import RoomService

        movies = MovieService().get_all_movies()
        rooms = RoomService().get_all()


        return movies, rooms

    def save(self, mode, st_id, movie_id, room_id, date_str, time_str, price):
        return self.service.save_showtime(mode, st_id, movie_id, room_id, date_str, time_str, price)

    def delete(self, st_id):
        return self.service.delete_showtime(st_id)