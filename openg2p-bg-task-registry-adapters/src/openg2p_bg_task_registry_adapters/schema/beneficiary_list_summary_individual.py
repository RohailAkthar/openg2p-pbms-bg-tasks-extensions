from typing import Optional

from pydantic import BaseModel

from .beneficiary_list_summary import BeneficiaryListSummaryPayload


class BeneficiaryListSummaryIndividual(BaseModel):
    age_mean: Optional[float] = None
    age_q1: Optional[float] = None
    age_q2: Optional[float] = None
    age_q3: Optional[float] = None
    female_count: Optional[int] = None
    male_count: Optional[int] = None
    plw_count: Optional[int] = None
    disabled_count: Optional[int] = None
    entitlement_amount_q1: Optional[dict] = None
    entitlement_amount_q2: Optional[dict] = None
    entitlement_amount_q3: Optional[dict] = None


class BeneficiaryListSummaryIndividualPayload(BeneficiaryListSummaryPayload):
    registry_summary: BeneficiaryListSummaryIndividual
