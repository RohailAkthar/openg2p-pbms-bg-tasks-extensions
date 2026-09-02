import math
from typing import List, Optional, Tuple

import numpy as np
from fastapi_cache.decorator import cache
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..cache import beneficiary_count_key_builder
from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryIndividual as BeneficiaryListSummaryIndividualModel,
    G2PRegisterIndividual,
)
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryIndividual,
    BeneficiaryListSummaryIndividualPayload,
    G2PRegisterIndividualPayload,
)


class RegistryIndividual(RegistryInterface):
    """Fetches individual registry data and computes summary statistics for Nigeria NSR"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryIndividualPayload:
        summary_result = await bg_task_session.execute(
            select(BeneficiaryListSummaryIndividualModel).where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        individual_summary = summary_result.scalars().first()

        if not individual_summary:
            return BeneficiaryListSummaryIndividualPayload(
                beneficiary_list_summary=BeneficiaryListSummary(
                    id="",
                    program_id="",
                    program_mnemonic="",
                    target_registry="individual",
                    beneficiary_list_id=beneficiary_list_id,
                    number_of_registrants=0,
                ),
                registry_summary=BeneficiaryListSummaryIndividual(),
            )

        return BeneficiaryListSummaryIndividualPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=individual_summary.id,
                program_id=individual_summary.program_id,
                program_mnemonic=individual_summary.program_mnemonic,
                target_registry=individual_summary.target_registry,
                beneficiary_list_id=individual_summary.beneficiary_list_id,
                number_of_registrants=individual_summary.number_of_registrants,
                date_created=individual_summary.date_created,
                total_disbursement_quantity=individual_summary.total_disbursement_quantity,
                average_entitlement_per_registrant=individual_summary.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryIndividual(
                age_mean=individual_summary.age_mean,
                age_q1=individual_summary.age_q1,
                age_q2=individual_summary.age_q2,
                age_q3=individual_summary.age_q3,
                female_count=individual_summary.female_count,
                male_count=individual_summary.male_count,
                plw_count=individual_summary.plw_count,
                disabled_count=individual_summary.disabled_count,
                entitlement_amount_q1=individual_summary.entitlement_amount_q1,
                entitlement_amount_q2=individual_summary.entitlement_amount_q2,
                entitlement_amount_q3=individual_summary.entitlement_amount_q3,
            ),
        )

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryIndividualPayload:
        individual_summary = (
            bg_task_session.query(BeneficiaryListSummaryIndividualModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )

        if not individual_summary:
            return BeneficiaryListSummaryIndividualPayload(
                beneficiary_list_summary=BeneficiaryListSummary(
                    id="",
                    program_id="",
                    program_mnemonic="",
                    target_registry="individual",
                    beneficiary_list_id=beneficiary_list_id,
                    number_of_registrants=0,
                ),
                registry_summary=BeneficiaryListSummaryIndividual(),
            )

        return BeneficiaryListSummaryIndividualPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=individual_summary.id,
                program_id=individual_summary.program_id,
                program_mnemonic=individual_summary.program_mnemonic,
                target_registry=individual_summary.target_registry,
                beneficiary_list_id=individual_summary.beneficiary_list_id,
                number_of_registrants=individual_summary.number_of_registrants,
                date_created=individual_summary.date_created,
                total_disbursement_quantity=individual_summary.total_disbursement_quantity,
                average_entitlement_per_registrant=individual_summary.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryIndividual(
                age_mean=individual_summary.age_mean,
                age_q1=individual_summary.age_q1,
                age_q2=individual_summary.age_q2,
                age_q3=individual_summary.age_q3,
                female_count=individual_summary.female_count,
                male_count=individual_summary.male_count,
                plw_count=individual_summary.plw_count,
                disabled_count=individual_summary.disabled_count,
                entitlement_amount_q1=individual_summary.entitlement_amount_q1,
                entitlement_amount_q2=individual_summary.entitlement_amount_q2,
                entitlement_amount_q3=individual_summary.entitlement_amount_q3,
            ),
        )

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
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ) -> Tuple[BeneficiarySearchResponsePayload, int]:
        registrant_details_result = await bg_task_session.execute(
            select(BeneficiaryListDetails.registrant_details).where(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
            )
        )
        registrant_details_rows = registrant_details_result.scalars().all()
        registrant_ids = []
        for details_batch in registrant_details_rows:
            if details_batch:
                for registrant in details_batch:
                    registrant_ids.append(registrant["registrant_id"])

        if not registrant_ids:
            return BeneficiarySearchResponsePayload(beneficiary_count=0, beneficiaries=[]), 0

        (
            individual_search_query,
            individual_search_params,
        ) = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            "individual",
            search_query,
            order_by,
            page_size,
            page,
        )
        search_results = (
            (await sr_session.execute(individual_search_query, individual_search_params))
            .mappings()
            .all()
        )

        total_count: int = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = []
        if search_results:
            beneficiaries = [
                G2PRegisterIndividualPayload(
                    internal_record_id=ind.get("internal_record_id"),
                    functional_record_id=ind.get("functional_record_id"),
                    full_name=ind.get("full_name") or f"{ind.get('first_name', '')} {ind.get('last_name', '')}".strip(),
                    gender=ind.get("gender"),
                    estimated_age=ind.get("estimated_age"),
                    relationship_to_head=ind.get("relationship_to_head"),
                    disability_status=ind.get("disability_status"),
                    plw_status=ind.get("plw_status"),
                    primary_livelihood=ind.get("primary_livelihood"),
                    foundational_id_masked=ind.get("foundational_id_masked"),
                    record_status=ind.get("record_status"),
                )
                for ind in search_results
            ]

        response_payload = BeneficiarySearchResponsePayload(
            beneficiary_count=len(beneficiaries),
            beneficiaries=beneficiaries,
        )

        return response_payload, total_count

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: str,
    ) -> int:
        (
            count_query,
            count_params,
        ) = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, "individual", search_query
        )
        total_count = (
            await sr_session.execute(count_query, count_params)
        ).scalar_one()

        return total_count

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
        individual_summary = BeneficiaryListSummaryIndividualModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        ages = []
        female_c = 0
        male_c = 0
        plw_c = 0
        disabled_c = 0

        for b_detail in beneficiary_list_details:
            registrant_ids = [r["registrant_id"] for r in (b_detail.registrant_details or [])]
            if registrant_ids:
                registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
                for ind in registrants:
                    if ind.estimated_age is not None:
                        ages.append(ind.estimated_age)
                    if (ind.gender or "").lower() == "female":
                        female_c += 1
                    elif (ind.gender or "").lower() == "male":
                        male_c += 1
                    if ind.plw_status:
                        plw_c += 1
                    if (ind.disability_status or "").upper() in ("YES", "TRUE"):
                        disabled_c += 1

        individual_summary.female_count = female_c
        individual_summary.male_count = male_c
        individual_summary.plw_count = plw_c
        individual_summary.disabled_count = disabled_c

        if ages:
            arr = np.array(ages)
            individual_summary.age_mean = round(float(np.mean(arr)), 2)
            individual_summary.age_q1 = round(float(np.percentile(arr, 25)), 2)
            individual_summary.age_q2 = round(float(np.percentile(arr, 50)), 2)
            individual_summary.age_q3 = round(float(np.percentile(arr, 75)), 2)

        bg_task_session.add(individual_summary)

    def get_registrants_by_ids(
        self, registrant_ids: List, sr_session: Session
    ) -> List[G2PRegisterIndividual]:
        individuals = sr_session.query(G2PRegisterIndividual).filter(
            G2PRegisterIndividual.internal_record_id.in_(registrant_ids)
        )
        return list(individuals.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        query_with_id = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, "individual", sql_query
        )
        result = sr_session.execute(query_with_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(multiplier, target_registry="individual")
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        return int(result[0]) if result and result[0] is not None else 1

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        entitlements: dict[int, list[float]] = {}
        for detail in beneficiary_list_details:
            for reg in (detail.registrant_details or []):
                entitlement_dict = reg.get("entitlement", {})
                for b_id, val in entitlement_dict.items():
                    entitlements.setdefault(b_id, []).append(val)

        q1_dict = {}
        q2_dict = {}
        q3_dict = {}
        for b_id, values in entitlements.items():
            if values:
                arr = np.array(values)
                q1_dict[b_id] = round(float(np.percentile(arr, 25)), 2)
                q2_dict[b_id] = round(float(np.percentile(arr, 50)), 2)
                q3_dict[b_id] = round(float(np.percentile(arr, 75)), 2)

        bg_task_session.execute(
            update(BeneficiaryListSummaryIndividualModel)
            .where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                entitlement_amount_q1=q1_dict,
                entitlement_amount_q2=q2_dict,
                entitlement_amount_q3=q3_dict,
            )
        )
