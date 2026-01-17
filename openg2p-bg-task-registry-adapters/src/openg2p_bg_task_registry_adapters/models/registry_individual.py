from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String, cast
from sqlalchemy.orm import column_property, declared_attr, mapped_column


class G2PIndividualRegistry(G2PRegistry):
    __tablename__ = "res_partner"

    @declared_attr
    def link_registry_id(cls):
        # Safe alias for 'id' as 'link_registry_id' is not a separate column in res_partner
        return column_property(cast(cls.id, String))

    name = mapped_column(String, nullable=False)
    gender = mapped_column(String, nullable=True)  # 'male' or 'female'
    birthdate = mapped_column(Date, nullable=True)
