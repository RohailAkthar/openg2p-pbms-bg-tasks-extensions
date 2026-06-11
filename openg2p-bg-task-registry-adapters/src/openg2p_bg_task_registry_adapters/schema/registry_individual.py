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
    pensioner_id: Optional[str] = None
    nominee_first_name: Optional[str] = None
    nominee_middle_name: Optional[str] = None
    nominee_gender: Optional[str] = None
    nominee_zanid: Optional[str] = None
    nominee_region: Optional[str] = None
    nominee_district: Optional[str] = None
    street: Optional[str] = None
    phone: Optional[str] = None
    benf_post_code: Optional[str] = None
    disability: Optional[str] = None
    is_receiving_allowance: Optional[str] = None
    has_health_insurance: Optional[str] = None
    payment_mode: Optional[str] = None
    bank_name: Optional[str] = None
    account_num: Optional[str] = None
    account_name: Optional[str] = None
    mobile_wallet: Optional[str] = None
    other_pension: Optional[str] = None
    scheme_name: Optional[str] = None
    nominee_last_name: Optional[str] = None
    nominee_mobile: Optional[str] = None
    nominee_rel_benf: Optional[str] = None
    nominee_house_street: Optional[str] = None
    nominee_shehia: Optional[str] = None
    nominee_post_code: Optional[str] = None
