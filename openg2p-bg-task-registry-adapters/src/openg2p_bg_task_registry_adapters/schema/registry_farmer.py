from typing import Optional

from .registry import G2PRegistryPayload


class G2PFarmerRegistryPayload(G2PRegistryPayload):
    name: Optional[str] = None
    farmer_id: Optional[str] = None
    farmer_name: Optional[str] = None
    gender: Optional[str] = None
    crop_type: Optional[str] = None
    land_area: Optional[float] = None
    land_area_acres: Optional[float] = None
    pm_kisan_enrolled: Optional[bool] = None
    district: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
