from typing import Optional

from .registry import G2PRegistryPayload


class G2PRegisterHouseholdPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    household_head_name: Optional[str] = None
    headship_type: Optional[str] = None
    size_total: Optional[int] = None
    dwelling_type: Optional[str] = None
    water_source_type: Optional[str] = None
    sanitation_type: Optional[str] = None
    geo_lowest_level_value_id: Optional[str] = None
    record_status: Optional[str] = None
