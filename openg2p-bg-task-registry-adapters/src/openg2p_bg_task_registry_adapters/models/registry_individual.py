from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String
from sqlalchemy.orm import mapped_column


class G2PIndividualRegistry(G2PRegistry):
    __tablename__ = "res_partner"

    name = mapped_column(String, nullable=False)
    gender = mapped_column(String, nullable=True)  # 'male' or 'female'
    birthdate_date = mapped_column(Date, nullable=True)
