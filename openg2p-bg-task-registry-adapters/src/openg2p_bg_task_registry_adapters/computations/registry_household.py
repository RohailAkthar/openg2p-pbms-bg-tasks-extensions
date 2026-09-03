import json
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
    BeneficiaryListSummaryHousehold as BeneficiaryListSummaryHouseholdModel,
    G2PRegisterHousehold,
)
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryHouseholdPayload,
    G2PRegisterHouseholdPayload,
)


class RegistryHousehold(RegistryInterface):
    """Fetches household registry data and computes summary statistics for Nigeria NSR"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryHouseholdPayload:
        summary_result = await bg_task_session.execute(
            select(BeneficiaryListSummaryHouseholdModel).where(
                BeneficiaryListSummaryHouseholdModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        household_summary = summary_result.scalars().first()

        if not household_summary:
            return BeneficiaryListSummaryHouseholdPayload(
                beneficiary_list_summary=BeneficiaryListSummary(
                    id="",
                    program_id="",
                    program_mnemonic="",
                    target_registry="household",
                    beneficiary_list_id=beneficiary_list_id,
                    number_of_registrants=0,
                ),
                registry_summary=BeneficiaryListSummaryHousehold(),
            )

        return BeneficiaryListSummaryHouseholdPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=household_summary.id,
                program_id=household_summary.program_id,
                program_mnemonic=household_summary.program_mnemonic,
                target_registry=household_summary.target_registry,
                beneficiary_list_id=household_summary.beneficiary_list_id,
                number_of_registrants=household_summary.number_of_registrants,
                date_created=household_summary.date_created,
                total_disbursement_quantity=household_summary.total_disbursement_quantity,
                average_entitlement_per_registrant=household_summary.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryHousehold(
                household_size_mean=household_summary.household_size_mean,
                household_size_q1=household_summary.household_size_q1,
                household_size_q2=household_summary.household_size_q2,
                household_size_q3=household_summary.household_size_q3,
                overcrowding_mean=household_summary.overcrowding_mean,
                entitlement_amount_q1=household_summary.entitlement_amount_q1,
                entitlement_amount_q2=household_summary.entitlement_amount_q2,
                entitlement_amount_q3=household_summary.entitlement_amount_q3,
            ),
        )

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryHouseholdPayload:
        household_summary = (
            bg_task_session.query(BeneficiaryListSummaryHouseholdModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )

        if not household_summary:
            return BeneficiaryListSummaryHouseholdPayload(
                beneficiary_list_summary=BeneficiaryListSummary(
                    id="",
                    program_id="",
                    program_mnemonic="",
                    target_registry="household",
                    beneficiary_list_id=beneficiary_list_id,
                    number_of_registrants=0,
                ),
                registry_summary=BeneficiaryListSummaryHousehold(),
            )

        return BeneficiaryListSummaryHouseholdPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=household_summary.id,
                program_id=household_summary.program_id,
                program_mnemonic=household_summary.program_mnemonic,
                target_registry=household_summary.target_registry,
                beneficiary_list_id=household_summary.beneficiary_list_id,
                number_of_registrants=household_summary.number_of_registrants,
                date_created=household_summary.date_created,
                total_disbursement_quantity=household_summary.total_disbursement_quantity,
                average_entitlement_per_registrant=household_summary.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryHousehold(
                household_size_mean=household_summary.household_size_mean,
                household_size_q1=household_summary.household_size_q1,
                household_size_q2=household_summary.household_size_q2,
                household_size_q3=household_summary.household_size_q3,
                overcrowding_mean=household_summary.overcrowding_mean,
                entitlement_amount_q1=household_summary.entitlement_amount_q1,
                entitlement_amount_q2=household_summary.entitlement_amount_q2,
                entitlement_amount_q3=household_summary.entitlement_amount_q3,
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
            household_search_query,
            household_search_params,
        ) = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            "household",
            search_query,
            order_by,
            page_size,
            page,
        )
        search_results = (
            (await sr_session.execute(household_search_query, household_search_params))
            .mappings()
            .all()
        )

        total_count: int = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = []
        if search_results:
            for h in search_results:
                # 1. Location details (Region, District, Ward)
                geo_json = h.get("geo_code_hierarchy_json")
                region = None
                district = None
                ward = h.get("geo_lowest_level_value_id") or None

                if geo_json:
                    try:
                        geo_data = json.loads(geo_json) if isinstance(geo_json, str) else geo_json
                        if isinstance(geo_data, dict):
                            region = geo_data.get("region") or geo_data.get("state") or geo_data.get("admin_level_1") or geo_data.get("level_1")
                            district = geo_data.get("district") or geo_data.get("lga") or geo_data.get("admin_level_2") or geo_data.get("level_2")
                            ward = geo_data.get("ward") or geo_data.get("admin_level_3") or geo_data.get("level_3") or ward
                    except Exception:
                        pass

                if not region:
                    region = h.get("address_line_1")
                if not district:
                    district = h.get("lga_administrative_code")

                # 2. Contact Phone Number (in NSR, stored in address_line_2 or phone_number)
                contact_number = h.get("phone_number") or h.get("contact_phone_number") or h.get("address_line_2")

                beneficiaries.append(
                    G2PRegisterHouseholdPayload(
                        internal_record_id=h.get("internal_record_id"),
                        functional_record_id=h.get("functional_record_id"),
                        link_foundational_id=h.get("link_foundational_id"),
                        household_head_name=h.get("household_head_name"),
                        headship_type=h.get("headship_type"),
                        size_total=h.get("size_total"),
                        region=region,
                        district=district,
                        ward=ward,
                        contact_number=contact_number,
                        family_monthly_income=h.get("family_monthly_income"),
                        pregnant_member_present=h.get("pregnant_member_present"),
                    )
                )

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
            registrant_ids, "household", search_query
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
        household_summary = BeneficiaryListSummaryHouseholdModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        sizes = []
        overcrowdings = []

        for b_detail in beneficiary_list_details:
            registrant_ids = [r["registrant_id"] for r in (b_detail.registrant_details or [])]
            if registrant_ids:
                registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
                for h in registrants:
                    if h.size_total is not None:
                        sizes.append(h.size_total)
                    if h.overcrowding_indicator is not None:
                        overcrowdings.append(h.overcrowding_indicator)

        if sizes:
            arr = np.array(sizes)
            household_summary.household_size_mean = round(float(np.mean(arr)), 2)
            household_summary.household_size_q1 = round(float(np.percentile(arr, 25)), 2)
            household_summary.household_size_q2 = round(float(np.percentile(arr, 50)), 2)
            household_summary.household_size_q3 = round(float(np.percentile(arr, 75)), 2)

        if overcrowdings:
            arr_o = np.array(overcrowdings)
            household_summary.overcrowding_mean = round(float(np.mean(arr_o)), 2)

        bg_task_session.add(household_summary)

    def get_registrants_by_ids(
        self, registrant_ids: List, sr_session: Session
    ) -> List[G2PRegisterHousehold]:
        households = sr_session.query(G2PRegisterHousehold).filter(
            G2PRegisterHousehold.internal_record_id.in_(registrant_ids)
        )
        return list(households.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        query_with_id = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, "household", sql_query
        )
        result = sr_session.execute(query_with_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(multiplier, target_registry="household")
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
            update(BeneficiaryListSummaryHouseholdModel)
            .where(
                BeneficiaryListSummaryHouseholdModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                entitlement_amount_q1=q1_dict,
                entitlement_amount_q2=q2_dict,
                entitlement_amount_q3=q3_dict,
            )
        )
