from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String, cast
from sqlalchemy.orm import column_property, declared_attr, mapped_column


class G2PIndividualRegistry(G2PRegistry):
    __tablename__ = "res_partner"

    @declared_attr
    def link_registry_id(cls):
        return column_property(
            cast(cls.id, String).label("link_registry_id")
        )

    name = mapped_column(String, nullable=False)
    gender = mapped_column(String, nullable=True)
    birthdate = mapped_column(Date, nullable=True)
