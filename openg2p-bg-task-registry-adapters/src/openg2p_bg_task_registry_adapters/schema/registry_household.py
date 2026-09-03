from typing import Optional

from .registry import G2PRegistryPayload


class G2PRegisterHouseholdPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    link_foundational_id: Optional[str] = None
    household_head_name: Optional[str] = None
    headship_type: Optional[str] = None
    size_total: Optional[int] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    geo_lowest_level_value_id: Optional[str] = None
    phone_number: Optional[str] = None
    family_monthly_income: Optional[float] = None
    pregnant_member_present: Optional[bool] = None
    record_status: Optional[str] = None

