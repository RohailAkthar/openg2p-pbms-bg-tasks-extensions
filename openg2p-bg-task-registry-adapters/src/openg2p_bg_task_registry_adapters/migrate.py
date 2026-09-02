from .models import (
    BeneficiaryListSummaryFamilies,
    BeneficiaryListSummaryFarmer,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryIndividual,
    BeneficiaryListSummaryStudent,
)


def get_models():
    return [
        BeneficiaryListSummaryHousehold,
        BeneficiaryListSummaryIndividual,
        BeneficiaryListSummaryFamilies,
        BeneficiaryListSummaryStudent,
        BeneficiaryListSummaryFarmer,
    ]