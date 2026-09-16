from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, Float, String
from sqlalchemy.orm import mapped_column


class G2PFarmerRegistry(G2PRegistry):
    __tablename__ = "g2p_register_farmers"

    record_name = mapped_column(String, nullable=True)
    farmer_name = mapped_column(String, nullable=True)
    gender = mapped_column(String, nullable=True)  # 'male' or 'female'
    birth_date = mapped_column(Date, nullable=True)
    land_area_acres = mapped_column(Float, nullable=True)
    link_registry_id = mapped_column(String, nullable=True)

    @property
    def name(self):
        return self.farmer_name or self.record_name

    @property
    def land_area(self):
        return self.land_area_acres

    @property
    def annual_income(self):
        return None

    @property
    def no_of_cattle_heads(self):
        return 0

    @property
    def no_of_poultry_heads(self):
        return 0

