from datetime import date
from typing import Optional

from .registry import G2PRegistryPayload


class G2PFarmerRegistryPayload(G2PRegistryPayload):
    name: Optional[str] = None
    farmer_id: Optional[str] = None
    farmer_name: Optional[str] = None
    aadhaar_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    mobile_number: Optional[str] = None
    relation_name: Optional[str] = None
    crop_type: Optional[str] = None
    land_area: Optional[float] = None
    land_area_acres: Optional[float] = None
    land_ownership_type: Optional[str] = None
    pm_kisan_enrolled: Optional[bool] = None
    pmfby_enrolled: Optional[bool] = None
    bank_account_no: Optional[str] = None
    khata_number: Optional[str] = None
    khesra_number: Optional[str] = None
    khatiyan_number: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
