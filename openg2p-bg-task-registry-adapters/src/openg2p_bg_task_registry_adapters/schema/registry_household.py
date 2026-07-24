from datetime import date
from typing import Optional

from .registry import G2PRegistryPayload


from pydantic import BaseModel


class BeneficiaryListSummaryHousehold(BaseModel):
    total_male_heads: Optional[int] = 0
    total_female_heads: Optional[int] = 0
    average_household_size: Optional[float] = 0.0


class G2PHouseholdRegistryPayload(G2PRegistryPayload):
    name: Optional[str] = None
    household_id: Optional[str] = None
    household_size: Optional[int] = None
    head_name: Optional[str] = None
    head_gender: Optional[str] = None
    head_phone: Optional[str] = None
    head_dob: Optional[date] = None
    children_count: Optional[int] = None
    adult_count: Optional[int] = None
    has_pregnant_member: Optional[str] = None
    has_disabled_member: Optional[str] = None
    small_area_code: Optional[str] = None
    large_area_code: Optional[str] = None
