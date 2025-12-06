from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.service = AuthService()

    def login(self, username, password):
        return self.service.login(username, password)

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        return self.service.change_password(user_id, old_pass, new_pass, confirm_pass)