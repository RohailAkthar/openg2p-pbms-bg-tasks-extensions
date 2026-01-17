from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String, cast
from sqlalchemy.orm import mapped_column, column_property


class G2PIndividualRegistry(G2PRegistry):
    __tablename__ = "res_partner"

    # Safe alias for 'id' as 'link_registry_id' is not a separate column in res_partner
    # Safe alias for 'id' as 'link_registry_id' is not a separate column in res_partner
    link_registry_id = column_property(cast(G2PRegistry.id, String))

    name = mapped_column(String, nullable=False)
    gender = mapped_column(String, nullable=True)  # 'male' or 'female'
    birthdate = mapped_column(Date, nullable=True)
