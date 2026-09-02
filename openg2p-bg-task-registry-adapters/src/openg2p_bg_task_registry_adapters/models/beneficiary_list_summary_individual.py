from openg2p_bg_task_models.models import BeneficiaryListSummary
from sqlalchemy import JSON, Float, Integer
from sqlalchemy.orm import mapped_column


class BeneficiaryListSummaryIndividual(BeneficiaryListSummary):
    __tablename__ = "beneficiary_list_summary_individual"

    # Age Distribution
    age_mean = mapped_column(Float, nullable=True, default=0)
    age_q1 = mapped_column(Float, nullable=True, default=0)
    age_q2 = mapped_column(Float, nullable=True, default=0)
    age_q3 = mapped_column(Float, nullable=True, default=0)

    # Vulnerability Counts
    female_count = mapped_column(Integer, nullable=True, default=0)
    male_count = mapped_column(Integer, nullable=True, default=0)
    plw_count = mapped_column(Integer, nullable=True, default=0)
    disabled_count = mapped_column(Integer, nullable=True, default=0)

    # Entitlement Distribution
    entitlement_amount_q1 = mapped_column(JSON, nullable=True)
    entitlement_amount_q2 = mapped_column(JSON, nullable=True)
    entitlement_amount_q3 = mapped_column(JSON, nullable=True)
