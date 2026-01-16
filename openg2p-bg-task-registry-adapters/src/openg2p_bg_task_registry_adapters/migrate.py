from .models import BeneficiaryListSummaryFarmer, BeneficiaryListSummaryStudent,BeneficiaryListSummaryIndividual

def get_models():
    return [
        BeneficiaryListSummaryFarmer,
        BeneficiaryListSummaryStudent,
        BeneficiaryListSummaryIndividual,
    ]