from services.customer_service import CustomerService

class CustomerController:
    def __init__(self):
        self.service = CustomerService()

    def get_all(self):
        return self.service.get_all()

    def search(self, keyword):
        return self.service.search(keyword)

    def get_detail(self, customer_id):
        return self.service.get_detail(customer_id)

    def save(self, mode, customer_id, name, phone, email, dob, points, level):
        return self.service.save_customer(mode, customer_id, name, phone, email, dob, points, level)

    def delete(self, customer_id):
        return self.service.delete_customer(customer_id)