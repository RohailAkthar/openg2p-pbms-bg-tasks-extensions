import logging
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi_cache.decorator import cache
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from openg2p_pbms_models.models import Gender
from sqlalchemy import TextClause, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..cache import beneficiary_count_key_builder
from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryIndividual as BeneficiaryListSummaryIndividualModel,
    G2PIndividualRegistry,
)
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryIndividual,
    BeneficiaryListSummaryIndividualPayload,
    G2PIndividualRegistryPayload,
)

_logger = logging.getLogger("openg2p_bg_task_registry_adapters")


class RegistryIndividual(RegistryInterface):
    """Fetches individual data from res_partner (via ORM) and computes statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryIndividualPayload:
        _logger.info(f"Fetching summary for beneficiary_list_id: {beneficiary_list_id}")
        beneficiary_list_summary_individual = await bg_task_session.execute(
            select(BeneficiaryListSummaryIndividualModel).where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id == beneficiary_list_id
            )
        )
        beneficiary_list_summary_individual = beneficiary_list_summary_individual.scalars().first()

        if not beneficiary_list_summary_individual:
            raise ValueError(
                f"No summary found for beneficiary_list_id: {beneficiary_list_id}"
            )

        summary_individual_payload = BeneficiaryListSummaryIndividualPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_individual.id,
                program_id=beneficiary_list_summary_individual.program_id,
                program_mnemonic=beneficiary_list_summary_individual.program_mnemonic,
                target_registry=beneficiary_list_summary_individual.target_registry,
                beneficiary_list_id=beneficiary_list_summary_individual.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_individual.number_of_registrants,
                date_created=beneficiary_list_summary_individual.date_created,
                total_disbursement_quantity=beneficiary_list_summary_individual.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_individual.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryIndividual(
                age_mean=f"{beneficiary_list_summary_individual.age_mean} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_mean is not None
                else None,
                age_q1=f"{beneficiary_list_summary_individual.age_q1} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q1 is not None
                else None,
                age_q2=f"{beneficiary_list_summary_individual.age_q2} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q2 is not None
                else None,
                age_q3=f"{beneficiary_list_summary_individual.age_q3} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q3 is not None
                else None,
                average_entitlement_female=beneficiary_list_summary_individual.average_entitlement_female,
                average_entitlement_male=beneficiary_list_summary_individual.average_entitlement_male,
                entitlement_amount_q1=beneficiary_list_summary_individual.entitlement_amount_q1,
                entitlement_amount_q2=beneficiary_list_summary_individual.entitlement_amount_q2,
                entitlement_amount_q3=beneficiary_list_summary_individual.entitlement_amount_q3,
                entitlement_amount_male_q1=beneficiary_list_summary_individual.entitlement_amount_male_q1,
                entitlement_amount_male_q2=beneficiary_list_summary_individual.entitlement_amount_male_q2,
                entitlement_amount_male_q3=beneficiary_list_summary_individual.entitlement_amount_male_q3,
                entitlement_amount_female_q1=beneficiary_list_summary_individual.entitlement_amount_female_q1,
                entitlement_amount_female_q2=beneficiary_list_summary_individual.entitlement_amount_female_q2,
                entitlement_amount_female_q3=beneficiary_list_summary_individual.entitlement_amount_female_q3,
            ),
        )
        return summary_individual_payload

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryIndividualPayload:
        beneficiary_list_summary_individual = (
            bg_task_session.query(BeneficiaryListSummaryIndividualModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )

        if not beneficiary_list_summary_individual:
            raise ValueError(
                f"No summary found for beneficiary_list_id: {beneficiary_list_id}"
            )

        summary_individual_payload = BeneficiaryListSummaryIndividualPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_individual.id,
                program_id=beneficiary_list_summary_individual.program_id,
                program_mnemonic=beneficiary_list_summary_individual.program_mnemonic,
                target_registry=beneficiary_list_summary_individual.target_registry,
                beneficiary_list_id=beneficiary_list_summary_individual.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_individual.number_of_registrants,
                date_created=beneficiary_list_summary_individual.date_created,
                total_disbursement_quantity=beneficiary_list_summary_individual.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_individual.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryIndividual(
                age_mean=f"{beneficiary_list_summary_individual.age_mean} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_mean is not None
                else None,
                age_q1=f"{beneficiary_list_summary_individual.age_q1} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q1 is not None
                else None,
                age_q2=f"{beneficiary_list_summary_individual.age_q2} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q2 is not None
                else None,
                age_q3=f"{beneficiary_list_summary_individual.age_q3} {beneficiary_list_summary_individual.age_units}"
                if beneficiary_list_summary_individual.age_q3 is not None
                else None,
                average_entitlement_female=beneficiary_list_summary_individual.average_entitlement_female,
                average_entitlement_male=beneficiary_list_summary_individual.average_entitlement_male,
                entitlement_amount_q1=beneficiary_list_summary_individual.entitlement_amount_q1,
                entitlement_amount_q2=beneficiary_list_summary_individual.entitlement_amount_q2,
                entitlement_amount_q3=beneficiary_list_summary_individual.entitlement_amount_q3,
                entitlement_amount_male_q1=beneficiary_list_summary_individual.entitlement_amount_male_q1,
                entitlement_amount_male_q2=beneficiary_list_summary_individual.entitlement_amount_male_q2,
                entitlement_amount_male_q3=beneficiary_list_summary_individual.entitlement_amount_male_q3,
                entitlement_amount_female_q1=beneficiary_list_summary_individual.entitlement_amount_female_q1,
                entitlement_amount_female_q2=beneficiary_list_summary_individual.entitlement_amount_female_q2,
                entitlement_amount_female_q3=beneficiary_list_summary_individual.entitlement_amount_female_q3,
            ),
        )

        return summary_individual_payload

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
        order_by: str = "id asc",
    ) -> BeneficiarySearchResponsePayload:
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

        individual_search_query, individual_search_params = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )
        individual_search_results = (
            (await sr_session.execute(individual_search_query, individual_search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = []
        if individual_search_results:
            beneficiaries = [
                G2PIndividualRegistryPayload(
                    id=individual["id"],
                    link_registry_id=individual["registrant_id_str"],
                    name=individual["name"],
                    gender=individual["gender"],
                    birthdate_date=individual["birthdate_date"],
                )
                for individual in individual_search_results
            ]

        response_payload = BeneficiarySearchResponsePayload(
            total_beneficiary_count=total_beneficiary_count,
            page=page,
            page_size=page_size,
            beneficiaries=beneficiaries,
        )

        return response_payload

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: Optional[str] = None,
    ) -> int:
        beneficiary_count_query, beneficiary_count_params = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, "individual", search_query
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
        ages = []
        for beneficiary_list_detail in beneficiary_list_details:
            registrant_ids = []
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail["registrant_id"] = str(registrant_detail["registrant_id"])
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant_ids.append(registrant_detail.registrant_id)

            registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
            for registrant in registrants:
                if registrant.birthdate_date:
                    ages.append(self.calculate_age(registrant.birthdate_date))

        individual_summary = BeneficiaryListSummaryIndividualModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        if ages:
            ages_array = np.array(ages)
            individual_summary.age_q1 = round(float(np.percentile(ages_array, 25, method="midpoint")), 2)
            individual_summary.age_q2 = round(float(np.percentile(ages_array, 50, method="midpoint")), 2)
            individual_summary.age_q3 = round(float(np.percentile(ages_array, 75, method="midpoint")), 2)
            individual_summary.age_mean = round(float(np.mean(ages_array)), 2)

        bg_task_session.add(individual_summary)

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PIndividualRegistry]:
        individuals = sr_session.query(G2PIndividualRegistry).filter(
            G2PIndividualRegistry.id.in_(registrant_ids)
        )

        return list(individuals.yield_per(500))

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, "individual", sql_query
        )
        result = sr_session.execute(sql_query_with_registrant_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(
            multiplier, target_registry="individual"
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

        registrant_map_from_registry: Dict[str, G2PIndividualRegistry] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            registrant_ids = []
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail["registrant_id"] = str(registrant_detail["registrant_id"])
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant_ids.append(registrant_detail.registrant_id)

            registrants_list: List[G2PIndividualRegistry] = self.get_registrants_by_ids(
                registrant_ids, sr_session
            )

            for registrant in registrants_list:
                registrant_map_from_registry[str(registrant.id)] = registrant

        # Collect entitlements per benefit_code_id
        entitlements: Dict[int, List[float]] = {}
        entitlements_male: Dict[int, List[float]] = {}
        entitlements_female: Dict[int, List[float]] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail["registrant_id"] = str(registrant_detail["registrant_id"])
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant = registrant_map_from_registry.get(
                    str(registrant_detail.registrant_id)
                )
                gender = registrant.gender if registrant else None

                for benefit_code_id, value in registrant_detail.entitlement.items():
                    entitlements.setdefault(benefit_code_id, []).append(value)
                    if gender == Gender.MALE.value:
                        entitlements_male.setdefault(benefit_code_id, []).append(value)
                    elif gender == Gender.FEMALE.value:
                        entitlements_female.setdefault(benefit_code_id, []).append(value)
                    else:
                        _logger.warning(f"Invalid or missing gender for registrant: {registrant_detail.registrant_id}")

        entitlement_stats = self.compute_stats_dict(entitlements)
        entitlement_male_stats = self.compute_stats_dict(entitlements_male)
        entitlement_female_stats = self.compute_stats_dict(entitlements_female)

        bg_task_session.execute(
            update(BeneficiaryListSummaryIndividualModel)
            .where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(entitlement_stats["total"]),
                average_entitlement_per_person=dict(entitlement_stats["average"]),
                entitlement_amount_q1=dict(entitlement_stats["q1"]),
                entitlement_amount_q2=dict(entitlement_stats["q2"]),
                entitlement_amount_q3=dict(entitlement_stats["q3"]),
                average_entitlement_male=dict(entitlement_male_stats["average"]),
                entitlement_amount_male_q1=dict(entitlement_male_stats["q1"]),
                entitlement_amount_male_q2=dict(entitlement_male_stats["q2"]),
                entitlement_amount_male_q3=dict(entitlement_male_stats["q3"]),
                average_entitlement_female=dict(entitlement_female_stats["average"]),
                entitlement_amount_female_q1=dict(entitlement_female_stats["q1"]),
                entitlement_amount_female_q2=dict(entitlement_female_stats["q2"]),
                entitlement_amount_female_q3=dict(entitlement_female_stats["q3"]),
            )
        )

    # ===============================
    # SQL Construction Overrides
    # ===============================
    def construct_multiplier_sql_query(
        self, multiplier: str, target_registry: str
    ) -> TextClause:
        if not multiplier or multiplier == "none":
            return None

        # Override due to res_partner mapping
        sql_query = text(
            f"""
            SELECT {multiplier}::TEXT FROM res_partner
            WHERE id = :registrant_id
            """
        )
        return sql_query

    def construct_beneficiary_search_sql_query(
        self,
        registrant_ids: List[str],
        target_registry: str,
        where_clause: str,
        order_by: str,
        page_size: int,
        page: int,
    ) :
        if not registrant_ids:
            return None, {}

        where_clause = where_clause.replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")

        # Override due to res_partner mapping
        table_name = "res_partner"
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT *, id::TEXT as registrant_id_str FROM {table_name}
            WHERE id IN ({registrant_placeholders}) {where_clause_sql}
            ORDER BY {order_by}
            OFFSET :offset
            LIMIT :limit
        """
        )

        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }
        params.update({"offset": page_size * (page - 1), "limit": page_size})

        return sql_query, params

    def construct_beneficiary_search_count_sql_query(
        self, registrant_ids: List[str], target_registry: str, where_clause: str
    ) :
        if not registrant_ids:
            return None, {}

        where_clause = where_clause.replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")

        # Override due to res_partner mapping
        table_name = "res_partner"
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE id IN ({registrant_placeholders}) {where_clause_sql}
        """
        )

        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }

        return sql_query, params

    def construct_get_is_registrant_entitled_sql_query(
        self, registrant_id: str, target_registry: str, sql_query: str
    ) -> TextClause:
        sql_query = sql_query.strip()

        if not registrant_id:
            raise ValueError("registrant_id cannot be None or zero")
        if not sql_query.upper().startswith("SELECT"):
            raise ValueError("Invalid SQL query: Must be a valid SELECT statement")

        # Override due to res_partner mapping
        if "WHERE" in sql_query.upper():
            sql_query += f" AND res_partner.id = :registrant_id"
        else:
            sql_query += f" WHERE res_partner.id = :registrant_id"

        params = {"registrant_id": registrant_id}

        return text(sql_query).params(**params)
