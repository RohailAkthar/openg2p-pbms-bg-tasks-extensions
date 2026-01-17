from datetime import date
from typing import Optional

from .registry import G2PRegistryPayload


class G2PIndividualRegistryPayload(G2PRegistryPayload):
    name: str
    gender: Optional[str] = None
    birthdate: Optional[date]
