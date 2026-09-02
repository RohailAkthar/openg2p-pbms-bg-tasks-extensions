from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryHousehold(BaseModel):
    household_size_mean: Optional[float] = None
    household_size_q1: Optional[float] = None
    household_size_q2: Optional[float] = None
    household_size_q3: Optional[float] = None
    overcrowding_mean: Optional[float] = None
    entitlement_amount_q1: Optional[dict] = None
    entitlement_amount_q2: Optional[dict] = None
    entitlement_amount_q3: Optional[dict] = None


class BeneficiaryListSummaryHouseholdPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryHousehold
