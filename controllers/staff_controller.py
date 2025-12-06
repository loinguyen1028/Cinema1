from services.staff_service import StaffService

class StaffController:
    def __init__(self):
        self.service = StaffService()

    def get_all(self):
        return self.service.get_all()

    def search(self, keyword):
        return self.service.search(keyword)

    def get_roles(self):
        return self.service.get_roles()

    def save(self, mode, staff_id, data):
        return self.service.save_staff(mode, staff_id, data)

    def delete(self, staff_id):
        return self.service.delete_staff(staff_id)

    def reset_password(self, staff_id, new_pass, confirm_pass):
        return self.service.reset_password(staff_id, new_pass, confirm_pass)