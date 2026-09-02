from enum import Enum
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class G2PRegistry(BaseORMModel):
    __abstract__ = True
    internal_record_id: Mapped[str] = mapped_column(String, primary_key=True)
