import logging
from typing import Any, Dict, List, Optional, Tuple

from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..interface import RegistryInterface
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryHousehold,
    BeneficiaryListSummaryPayload,
    G2PHouseholdRegistryPayload,
)

_logger = logging.getLogger("openg2p_bg_task_registry_adapters")


class RegistryHousehold(RegistryInterface):
    """Fetches household data and computes summary statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryPayload:
        _logger.info(f"Fetching summary for household beneficiary_list_id: {beneficiary_list_id}")
        count = 0
        program_id = 1
        program_mnemonic = "HOUSEHOLD"
        total_male_heads = 0
        total_female_heads = 0
        average_household_size = 0.0

        try:
            result = await bg_task_session.execute(
                select(BeneficiaryListDetails).where(
                    BeneficiaryListDetails.beneficiary_list_id == str(beneficiary_list_id)
                )
            )
            detail = result.scalars().first()
            if detail:
                count = detail.number_of_registrants or len(detail.registrant_details or [])
                details_list = detail.registrant_details or []
                registrant_ids = []
                for reg in details_list:
                    reg_id = reg.get("registrant_id") if isinstance(reg, dict) else getattr(reg, "registrant_id", None)
                    if reg_id:
                        registrant_ids.append(str(reg_id))

                try:
                    if registrant_ids:
                        placeholders = ", ".join([f":id_{i}" for i in range(len(registrant_ids))])
                        params = {f"id_{i}": registrant_ids[i] for i in range(len(registrant_ids))}
                        sql = text(f"SELECT head_gender, household_size FROM g2p_household_registry WHERE link_registry_id IN ({placeholders}) OR household_id IN ({placeholders})")
                        rows = (await bg_task_session.execute(sql, params)).fetchall()
                    else:
                        sql = text("SELECT head_gender, household_size FROM g2p_household_registry")
                        rows = (await bg_task_session.execute(sql)).fetchall()
                    
                    total_size = 0.0
                    for row in rows:
                        gender = str(row[0] or "").lower()
                        if gender.startswith("m"):
                            total_male_heads += 1
                        elif gender.startswith("f"):
                            total_female_heads += 1
                        
                        if row[1] is not None:
                            try:
                                total_size += float(row[1])
                            except (ValueError, TypeError):
                                pass
                    calc_denom = count if count > 0 else len(rows)
                    if calc_denom > 0 and total_size > 0:
                        average_household_size = round(total_size / calc_denom, 2)
                except Exception as sr_err:
                    _logger.error(f"Error querying live household stats from SR: {sr_err}")

        except Exception as e:
            _logger.error(f"Error fetching registrant details in get_summary: {e}")

        return BeneficiaryListSummaryPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_id,
                program_id=program_id,
                program_mnemonic=program_mnemonic,
                target_registry="household",
                beneficiary_list_id=beneficiary_list_id,
                number_of_registrants=count,
                date_created=None,
            ),
            registry_summary=BeneficiaryListSummaryHousehold(
                total_male_heads=total_male_heads,
                total_female_heads=total_female_heads,
                average_household_size=average_household_size,
            ),
        )

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryPayload:
        _logger.info(f"Fetching sync summary for household beneficiary_list_id: {beneficiary_list_id}")
        count = 0
        program_id = 1
        program_mnemonic = "HOUSEHOLD"
        total_male_heads = 0
        total_female_heads = 0
        average_household_size = 0.0
        try:
            detail = bg_task_session.query(BeneficiaryListDetails).filter(
                BeneficiaryListDetails.beneficiary_list_id == str(beneficiary_list_id)
            ).first()
            if detail:
                count = detail.number_of_registrants or len(detail.registrant_details or [])
                details_list = detail.registrant_details or []
                registrant_ids = [str(reg.get("registrant_id")) for reg in details_list if isinstance(reg, dict) and reg.get("registrant_id")]
                if registrant_ids:
                    placeholders = ", ".join([f":id_{i}" for i in range(len(registrant_ids))])
                    params = {f"id_{i}": registrant_ids[i] for i in range(len(registrant_ids))}
                    sql = text(f"SELECT head_gender, household_size FROM g2p_household_registry WHERE link_registry_id IN ({placeholders}) OR household_id IN ({placeholders})")
                else:
                    sql = text("SELECT head_gender, household_size FROM g2p_household_registry")
                    params = {}
                rows = bg_task_session.execute(sql, params).fetchall()
                total_size = 0.0
                for row in rows:
                    gender = str(row[0] or "").lower()
                    if gender.startswith("m"):
                        total_male_heads += 1
                    elif gender.startswith("f"):
                        total_female_heads += 1
                    if row[1] is not None:
                        try:
                            total_size += float(row[1])
                        except (ValueError, TypeError):
                            pass
                calc_denom = count if count > 0 else len(rows)
                if calc_denom > 0 and total_size > 0:
                    average_household_size = round(total_size / calc_denom, 2)
        except Exception as e:
            _logger.error(f"Error fetching sync registrant details: {e}")

        return BeneficiaryListSummaryPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_id,
                program_id=program_id,
                program_mnemonic=program_mnemonic,
                target_registry="household",
                beneficiary_list_id=beneficiary_list_id,
                number_of_registrants=count,
                date_created=None,
            ),
            registry_summary=BeneficiaryListSummaryHousehold(
                total_male_heads=total_male_heads,
                total_female_heads=total_female_heads,
                average_household_size=average_household_size,
            ),
        )

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
        _logger.info(f"Computing eligibility statistics for household beneficiary list id: {base_summary.beneficiary_list_id}")

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        _logger.info(f"Computing entitlement statistics for household beneficiary list id: {beneficiary_list_id}")

    # =================
    # Registry methods
    # =================
    def get_registrants_by_ids(
        self, registrant_ids: List, sr_session: Session
    ) -> List:
        if not registrant_ids:
            return []
        query = text(
            "SELECT * FROM g2p_household_registry WHERE link_registry_id IN :ids"
        )
        results = sr_session.execute(query, {"ids": tuple(registrant_ids)}).fetchall()
        return list(results)

    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        if not registrant_id or not sql_query:
            return False
        constructed_query = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, "household", sql_query
        )
        result = sr_session.execute(constructed_query).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none" or not registrant_id:
            return 1
        constructed_query = self.construct_multiplier_sql_query(multiplier, "household")
        result = sr_session.execute(constructed_query, {"registrant_id": registrant_id}).fetchone()
        if result and result[0] is not None:
            try:
                return int(result[0])
            except (ValueError, TypeError):
                return 1
        return 1

    # ==============================
    # Beneficiary Search API Methods
    # ==============================
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "link_registry_id asc",
    ) -> BeneficiarySearchResponsePayload:
        if not order_by or "id asc" in order_by or order_by == "id":
            order_by = "link_registry_id asc"
        elif "id desc" in order_by:
            order_by = "link_registry_id desc"

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

        household_search_query, household_search_params = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )
        household_search_results = (
            (await sr_session.execute(household_search_query, household_search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count = 0
        count_query, count_params = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, target_registry, search_query
        )
        if count_query:
            try:
                count_res = (await sr_session.execute(count_query, count_params)).scalar()
                if count_res is not None and count_res > 0:
                    total_beneficiary_count = count_res
            except Exception as cnt_err:
                _logger.error(f"Error calculating beneficiary count: {cnt_err}")
                total_beneficiary_count = len(registrant_ids) or len(household_search_results)
        if total_beneficiary_count == 0:
            total_beneficiary_count = len(registrant_ids) or len(household_search_results)

        beneficiaries = []
        if household_search_results:
            beneficiaries = [
                G2PHouseholdRegistryPayload(
                    id=hh.get("id", idx + 1),
                    link_registry_id=str(hh.get("link_registry_id", "")),
                    name=hh.get("name") or hh.get("head_name") or "Household Record",
                    household_id=hh.get("household_id"),
                    household_size=hh.get("household_size"),
                    head_name=hh.get("head_name"),
                    head_gender=hh.get("head_gender"),
                    head_phone=hh.get("head_phone"),
                    head_dob=hh.get("head_dob"),
                    children_count=hh.get("children_count"),
                    adult_count=hh.get("adult_count"),
                    has_pregnant_member=hh.get("has_pregnant_member"),
                    has_disabled_member=hh.get("has_disabled_member"),
                    small_area_code=hh.get("small_area_code"),
                    large_area_code=hh.get("large_area_code"),
                )
                for idx, hh in enumerate(household_search_results)
            ]

        response_payload = BeneficiarySearchResponsePayload(
            beneficiary_count=total_beneficiary_count,
            total_beneficiary_count=total_beneficiary_count,
            page=page,
            page_size=page_size,
            beneficiaries=beneficiaries,
        )

        return response_payload, total_beneficiary_count
