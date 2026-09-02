from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, Integer
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryHousehold(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_household"

    # Household Size Distribution
    household_size_mean = mapped_column(Float, nullable=True, default=0)
    household_size_q1 = mapped_column(Float, nullable=True, default=0)
    household_size_q2 = mapped_column(Float, nullable=True, default=0)
    household_size_q3 = mapped_column(Float, nullable=True, default=0)

    # Overcrowding Index
    overcrowding_mean = mapped_column(Float, nullable=True, default=0)

    # Entitlement Distribution
    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
