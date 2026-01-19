from datetime import date
from typing import Optional

from .registry import G2PRegistryPayload


class G2PIndividualRegistryPayload(G2PRegistryPayload):
    name: str
    gender: Optional[str] = None
    birthdate: Optional[date]
    region_name: Optional[str] = None
    district_name: Optional[str] = None
    benf_zan_id: Optional[str] = None
    nominee_first_name: Optional[str] = None
    nominee_gender: Optional[str] = None
    nominee_zanid: Optional[str] = None
    nominee_region: Optional[str] = None
    nominee_district: Optional[str] = None
