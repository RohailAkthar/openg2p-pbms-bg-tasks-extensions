from typing import Optional

from .registry import G2PRegistryPayload


class G2PRegisterIndividualPayload(G2PRegistryPayload):
    functional_record_id: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None
    estimated_age: Optional[int] = None
    relationship_to_head: Optional[str] = None
    disability_status: Optional[str] = None
    plw_status: Optional[bool] = None
    primary_livelihood: Optional[str] = None
    foundational_id_masked: Optional[str] = None
    record_status: Optional[str] = None
