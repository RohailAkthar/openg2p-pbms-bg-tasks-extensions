import math
from typing import List, Optional, Tuple

import numpy as np
from fastapi_cache.decorator import cache
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from openg2p_fastapi_common.schemas import G2PPaginationRequest
from openg2p_pbms_models.models import Gender
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..cache import beneficiary_count_key_builder
from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryFamilies as BeneficiaryListSummaryFamiliesModel,
)
from ..models import (
    G2PRegisterFamilies,
)
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryFamilies,
    BeneficiaryListSummaryFamiliesPayload,
    G2PRegisterFamiliesPayload,
)


class RegisterFamilies(RegistryInterface):
    """Fetches families data and computes summary statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryFamiliesPayload:
        beneficiary_list_summary_families = await bg_task_session.execute(
            select(BeneficiaryListSummaryFamiliesModel).where(
                BeneficiaryListSummaryFamiliesModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        beneficiary_list_summary_families = (
            beneficiary_list_summary_families.scalars().first()
        )

        # Guard: summary row may not exist yet if the worker hasn't finished
        if beneficiary_list_summary_families is None:
            return None

        summary_families_payload = BeneficiaryListSummaryFamiliesPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_families.id,
                program_id=beneficiary_list_summary_families.program_id,
                program_mnemonic=beneficiary_list_summary_families.program_mnemonic,
                target_registry=beneficiary_list_summary_families.target_registry,
                beneficiary_list_id=beneficiary_list_summary_families.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_families.number_of_registrants,
                date_created=beneficiary_list_summary_families.date_created,
                total_disbursement_quantity=beneficiary_list_summary_families.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_families.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryFamilies(
                number_of_eligible_households=beneficiary_list_summary_families.number_of_registrants,
                entitlement_amount_q3=beneficiary_list_summary_families.entitlement_amount_q3,
                entitlement_amount_q2=beneficiary_list_summary_families.entitlement_amount_q2,
                entitlement_amount_q1=beneficiary_list_summary_families.entitlement_amount_q1,
            ),
        )

        return summary_families_payload

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryFamiliesPayload:
        beneficiary_list_summary_families = (
            bg_task_session.query(BeneficiaryListSummaryFamiliesModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )

        # Guard: summary row may not exist yet if the worker hasn't finished
        if beneficiary_list_summary_families is None:
            return None

        summary_families_payload = BeneficiaryListSummaryFamiliesPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_families.id,
                program_id=beneficiary_list_summary_families.program_id,
                program_mnemonic=beneficiary_list_summary_families.program_mnemonic,
                target_registry=beneficiary_list_summary_families.target_registry,
                beneficiary_list_id=beneficiary_list_summary_families.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_families.number_of_registrants,
                date_created=beneficiary_list_summary_families.date_created,
                total_disbursement_quantity=beneficiary_list_summary_families.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_families.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryFamilies(
                number_of_eligible_households=beneficiary_list_summary_families.number_of_registrants,
                entitlement_amount_q3=beneficiary_list_summary_families.entitlement_amount_q3,
                entitlement_amount_q2=beneficiary_list_summary_families.entitlement_amount_q2,
                entitlement_amount_q1=beneficiary_list_summary_families.entitlement_amount_q1,
            ),
        )
        return summary_families_payload

    # ==============================
    # Beneficiary Search API Methods
    # ==============================
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_query,
        page=1,
        page_size=10,
        order_by="internal_record_id asc",
    ) -> Tuple[BeneficiarySearchResponsePayload, int]:
        registrant_details = await bg_task_session.execute(
            select(BeneficiaryListDetails.registrant_details).where(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
            )
        )
        registrant_details = registrant_details.scalars().all()
        registrant_ids = []
        for registrant_detail in registrant_details:
            for registrant in registrant_detail:
                registrant_ids.append(registrant["registrant_id"])

        (
            families_search_query,
            families_search_params,
        ) = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )
        families_search_results = (
            (await sr_session.execute(families_search_query, families_search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count: int = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query, target_registry
        )
        beneficiaries = []
        if families_search_results:
            if target_registry == "gramstackhousehold":
                for row in families_search_results:
                    beneficiaries.append({
                        "internal_record_id": row.get("internal_record_id"),
                        "household_reference_name": row.get("household_reference_name"),
                        "house_reference_no": row.get("house_reference_no"),
                        "lokos_id": row.get("lokos_id"),
                        "applicant_name": row.get("applicant_name"),
                        "member_name": row.get("member_name"),
                        "gender": row.get("gender"),
                        "dob": str(row.get("dob")) if row.get("dob") else None,
                        "relationship_to_hoh": row.get("relationship_to_hoh"),
                        "mobile_number": row.get("mobile_number"),
                        "bank_account_no": row.get("bank_account_no"),
                        "ifsc": row.get("ifsc"),
                        "village": row.get("village"),
                        "gram_panchayat": row.get("gram_panchayat"),
                        "block": row.get("block"),
                        "district": row.get("district"),
                        "pds_classification": row.get("pds_classification"),
                        "aadhaar_number": row.get("aadhaar_number"),
                        "member_id": row.get("member_id"),
                        "shg_id": row.get("shg_id"),
                        "shg_name": row.get("shg_name"),
                        "vo_name": row.get("vo_name"),
                        "clf_name": row.get("clf_name"),
                        "shg_role": row.get("shg_role"),
                        "monthly_savings_amount": float(row.get("monthly_savings_amount") or 0),
                        "internal_loan_outstanding": float(row.get("internal_loan_outstanding") or 0),
                        "ccl_limit": float(row.get("ccl_limit") or 0),
                        "ccl_utilized": float(row.get("ccl_utilized") or 0),
                        "shg_grading": row.get("shg_grading"),
                        "scheme_code": row.get("scheme_code"),
                        "scheme_name": row.get("scheme_name"),
                        "status": row.get("status"),
                        "applied_at": str(row.get("applied_at")) if row.get("applied_at") else None,
                    })
            else:
                beneficiaries = [
                    G2PRegisterFamiliesPayload(
                        internal_record_id=families["internal_record_id"],
                        functional_record_id=families.get("functional_record_id", ""),
                        family_name=families.get("family_name", ""),
                        type_of_housing=families.get("type_of_housing"),
                        house_condition=families.get("house_condition"),
                        sanitation_condition=families.get("sanitation_condition"),
                        water_access=families.get("water_access"),
                        electricity_access=families.get("electricity_access"),
                        ethnic_group=families.get("ethnic_group"),
                        no_of_children=families.get("no_of_children"),
                        belong_to_protected_groups=families.get("belong_to_protected_groups"),
                        under_other_vulnerable_status=families.get("under_other_vulnerable_status"),
                    )
                    for families in families_search_results
                ]

        response_payload = BeneficiarySearchResponsePayload(
            beneficiary_count=len(beneficiaries),
            beneficiaries=beneficiaries,
        )

        return response_payload, total_beneficiary_count

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: str,
        target_registry: str = "gramstackhousehold",
    ) -> int:
        (
            beneficiary_count_query,
            beneficiary_count_params,
        ) = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, target_registry, search_query
        )
        total_beneficiary_count = (
            await sr_session.execute(beneficiary_count_query, beneficiary_count_params)
        ).scalar_one()

        return total_beneficiary_count

    # =================================
    # Eligibility Celery Worker Methods
    # =================================
    def compute_eligibility_statistics(
        self,
        beneficiary_list_details: List[BeneficiaryListDetails],
        base_summary,
        sr_session: Session,
        bg_task_session: Session,
    ):
        families_summary = BeneficiaryListSummaryFamiliesModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        # land_areas = []
        # annual_incomes = []

        # for beneficiary_list_detail in beneficiary_list_details:
        #     registrant_ids = []
        #     for registrant_detail in beneficiary_list_detail.registrant_details:
        #         registrant_detail = RegistrantDetails(**registrant_detail)
        #         registrant_ids.append(registrant_detail.registrant_id)

        #     registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
        #     for families in registrants:
        #         land_areas.append(families.land_area)
        #         annual_incomes.append(families.annual_income)

        # # Land Area Summary
        # if land_areas:
        #     land_areas_array = np.array(land_areas)
        #     families_summary.land_holding_mean = round(
        #         float(np.mean(land_areas_array)), 2
        #     )
        #     families_summary.land_holding_q1 = round(
        #         float(np.percentile(land_areas_array, 25, method="midpoint")), 2
        #     )
        #     families_summary.land_holding_q2 = round(
        #         float(np.percentile(land_areas_array, 50, method="midpoint")), 2
        #     )
        #     families_summary.land_holding_q3 = round(
        #         float(np.percentile(land_areas_array, 75, method="midpoint")), 2
        #     )

        # # Annual Income Summary
        # if annual_incomes:
        #     annual_incomes_array = np.array(annual_incomes)
        #     families_summary.annual_income_mean = round(
        #         float(np.mean(annual_incomes_array)), 2
        #     )
        #     families_summary.annual_income_q1 = round(
        #         float(np.percentile(annual_incomes_array, 25, method="midpoint")), 2
        #     )
        #     families_summary.annual_income_q2 = round(
        #         float(np.percentile(annual_incomes_array, 50, method="midpoint")), 2
        #     )
        #     families_summary.annual_income_q3 = round(
        #         float(np.percentile(annual_incomes_array, 75, method="midpoint")), 2
        #     )

        bg_task_session.add(families_summary)

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PRegisterFamilies]:
        familiess = sr_session.query(G2PRegisterFamilies).filter(
            G2PRegisterFamilies.internal_record_id.in_(registrant_ids)
        )

        return list(familiess.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = (
            self.construct_get_is_registrant_entitled_sql_query(
                registrant_id, "families", sql_query
            )
        )
        result = sr_session.execute(sql_query_with_registrant_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(
            multiplier, target_registry="families"
        )
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        multiplier_value: int = (
            int(result[0]) if result and result[0] is not None else 1
        )

        return multiplier_value

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        registrant_map_from_registry: dict[str, G2PRegisterFamilies] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            registrant_ids = []
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant_ids.append(registrant_detail.registrant_id)

            # Fething registrants in batches
            registrants_list: List[G2PRegisterFamilies] = self.get_registrants_by_ids(
                registrant_ids, sr_session
            )

            for registrant in registrants_list:
                registrant_map_from_registry[str(registrant.internal_record_id)] = registrant

        # Collect entitlements per benefit_code_id
        entitlements: dict[int, list[float]] = {}
        # entitlements_male: dict[int, list[float]] = {}
        # entitlements_female: dict[int, list[float]] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant = registrant_map_from_registry.get(
                    str(registrant_detail.registrant_id)
                )
                # gender = registrant.gender if registrant else None

                for benefit_code_id, value in registrant_detail.entitlement.items():
                    # All entitlements
                    entitlements.setdefault(benefit_code_id, []).append(value)
                #     # By gender
                #     if gender == Gender.MALE.value:
                #         entitlements_male.setdefault(benefit_code_id, []).append(value)
                #     elif gender == Gender.FEMALE.value:
                #         entitlements_female.setdefault(benefit_code_id, []).append(
                #             value
                #         )
                #     else:
                #         raise ValueError(f"Invalid gender: {gender}")

        # Compute all summary stats per benefit_code_id
        entitlement_stats = self.compute_stats_dict(entitlements)
        # entitlement_male_stats = self.compute_stats_dict(entitlements_male)
        # entitlement_female_stats = self.compute_stats_dict(entitlements_female)

        bg_task_session.execute(
            update(BeneficiaryListSummaryFamiliesModel)
            .where(
                BeneficiaryListSummaryFamiliesModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(entitlement_stats["total"]),
                average_entitlement_per_person=dict(entitlement_stats["average"]),
                entitlement_amount_q1=dict(entitlement_stats["q1"]),
                entitlement_amount_q2=dict(entitlement_stats["q2"]),
                entitlement_amount_q3=dict(entitlement_stats["q3"]),
                # average_entitlement_male=dict(entitlement_male_stats["average"]),
                # entitlement_amount_male_q1=dict(entitlement_male_stats["q1"]),
                # entitlement_amount_male_q2=dict(entitlement_male_stats["q2"]),
                # entitlement_amount_male_q3=dict(entitlement_male_stats["q3"]),
                # average_entitlement_female=dict(entitlement_female_stats["average"]),
                # entitlement_amount_female_q1=dict(entitlement_female_stats["q1"]),
                # entitlement_amount_female_q2=dict(entitlement_female_stats["q2"]),
                # entitlement_amount_female_q3=dict(entitlement_female_stats["q3"]),
            )
        )

    def compute_stats_dict(self, entitlements_dict: dict[int, list[float]]) -> dict:
        # Returns a dict of stats per benefit_code_id for each stat
        stats = {
            "average": {},
            "q1": {},
            "q2": {},
            "q3": {},
            "total": {},
        }
        for benefit_code_id, values in entitlements_dict.items():
            if not values:
                stats["average"][benefit_code_id] = 0.0
                stats["q1"][benefit_code_id] = 0.0
                stats["q2"][benefit_code_id] = 0.0
                stats["q3"][benefit_code_id] = 0.0
                stats["total"][benefit_code_id] = 0.0
            else:
                arr = np.array(values)
                stats["average"][benefit_code_id] = round(float(np.mean(arr)), 2)
                stats["q1"][benefit_code_id] = round(
                    float(np.percentile(arr, 25, method="midpoint")), 2
                )
                stats["q2"][benefit_code_id] = round(
                    float(np.percentile(arr, 50, method="midpoint")), 2
                )
                stats["q3"][benefit_code_id] = round(
                    float(np.percentile(arr, 75, method="midpoint")), 2
                )
                stats["total"][benefit_code_id] = float(np.sum(arr))
        return stats
