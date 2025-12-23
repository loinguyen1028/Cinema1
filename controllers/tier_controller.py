from services.tier_service import TierService

class TierController:
    def __init__(self):
        # Controller gọi Service (không gọi DAO trực tiếp nữa)
        self.service = TierService()

    def get_all(self):
        return self.service.get_all()

    def get_detail(self, tier_id):
        return self.service.get_detail(tier_id)

    def save(self, mode, tier_id, name, min_point, discount):
        # Chuyển tiếp yêu cầu sang Service xử lý
        return self.service.save_tier(mode, tier_id, name, min_point, discount)

    def delete(self, tier_id):
        return self.service.delete_tier(tier_id)