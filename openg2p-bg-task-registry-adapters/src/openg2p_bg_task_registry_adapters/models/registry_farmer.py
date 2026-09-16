from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Boolean, Date, Float, String
from sqlalchemy.orm import mapped_column


class G2PFarmerRegistry(G2PRegistry):
    __tablename__ = "g2p_register_farmers"

    record_name = mapped_column(String, nullable=True)
    functional_record_id = mapped_column(String, nullable=True)
    farmer_id = mapped_column(String, nullable=True)
    foundational_id = mapped_column(String, nullable=True)
    first_name = mapped_column(String, nullable=True)
    last_name = mapped_column(String, nullable=True)
    farmer_name = mapped_column(String, nullable=True)
    gender = mapped_column(String, nullable=True)  # 'male' or 'female'
    birth_date = mapped_column(Date, nullable=True)
    mobile_phone_number = mapped_column(String, nullable=True)
    farmer_mobile_number = mapped_column(String, nullable=True)
    relation_name = mapped_column(String, nullable=True)
    crop_type = mapped_column(String, nullable=True)
    land_area_acres = mapped_column(Float, nullable=True)
    land_ownership_type = mapped_column(String, nullable=True)
    pm_kisan_enrolled = mapped_column(Boolean, nullable=True)
    pmfby_enrolled = mapped_column(Boolean, nullable=True)
    farmer_bank_account_no = mapped_column(String, nullable=True)
    district = mapped_column(String, nullable=True)
    block = mapped_column(String, nullable=True)
    village = mapped_column(String, nullable=True)

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

