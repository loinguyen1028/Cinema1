from services.tier_service import TierService

class TierController:
    def __init__(self):

        self.service = TierService()

    def get_all(self):
        return self.service.get_all()

    def get_detail(self, tier_id):
        return self.service.get_detail(tier_id)

    def save(self, mode, tier_id, name, min_point, discount):

        return self.service.save_tier(mode, tier_id, name, min_point, discount)

    def delete(self, tier_id):
        return self.service.delete_tier(tier_id)