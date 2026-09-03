from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel


class BeneficiaryListSummary(BaseModel):
    id: Optional[str] = ""
    program_id: Optional[Union[int, str]] = 0
    program_mnemonic: Optional[str] = ""
    target_registry: Optional[str] = ""
    beneficiary_list_id: str
    number_of_registrants: int = 0
    date_created: Optional[datetime] = None
    total_disbursement_quantity: Optional[dict] = None
    average_entitlement_per_registrant: Optional[dict] = None


class BeneficiaryListSummaryPayload(BaseModel):
    beneficiary_list_summary: BeneficiaryListSummary
    registry_summary: Optional[Any] = None

