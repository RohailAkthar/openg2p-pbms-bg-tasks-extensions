import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
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
    """Registry adapter for individual beneficiaries"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryIndividualPayload:
        result = await bg_task_session.execute(
            select(BeneficiaryListSummaryIndividualModel).where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id
                == beneficiary_list_id
            )
        )
        summary = result.scalars().first()
        if not summary:
            raise ValueError(f"No summary found for {beneficiary_list_id}")

        return self._build_summary_payload(summary, formated=formated)

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session, formated: bool = False
    ) -> BeneficiaryListSummaryIndividualPayload:
        summary = (
            bg_task_session.query(BeneficiaryListSummaryIndividualModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )
        if not summary:
            raise ValueError(f"No summary found for {beneficiary_list_id}")

        return self._build_summary_payload(summary, formated=formated)

    def _build_summary_payload(
        self, summary: BeneficiaryListSummaryIndividualModel, formated: bool = False
    ) -> BeneficiaryListSummaryIndividualPayload:
        return BeneficiaryListSummaryIndividualPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=summary.id,
                program_id=summary.program_id,
                program_mnemonic=summary.program_mnemonic,
                target_registry=summary.target_registry,
                beneficiary_list_id=summary.beneficiary_list_id,
                number_of_registrants=summary.number_of_registrants,
                date_created=summary.date_created,
                total_disbursement_quantity=summary.total_disbursement_quantity,
                average_entitlement_per_registrant=summary.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryIndividual(
                age_mean=self._fmt_age(summary.age_mean, summary.age_units)
                if formated
                else (str(summary.age_mean) if summary.age_mean is not None else None),
                age_q1=self._fmt_age(summary.age_q1, summary.age_units)
                if formated
                else (str(summary.age_q1) if summary.age_q1 is not None else None),
                age_q2=self._fmt_age(summary.age_q2, summary.age_units)
                if formated
                else (str(summary.age_q2) if summary.age_q2 is not None else None),
                age_q3=self._fmt_age(summary.age_q3, summary.age_units)
                if formated
                else (str(summary.age_q3) if summary.age_q3 is not None else None),
                average_entitlement_female=summary.average_entitlement_female,
                average_entitlement_male=summary.average_entitlement_male,
                entitlement_amount_q1=summary.entitlement_amount_q1,
                entitlement_amount_q2=summary.entitlement_amount_q2,
                entitlement_amount_q3=summary.entitlement_amount_q3,
                entitlement_amount_male_q1=summary.entitlement_amount_male_q1,
                entitlement_amount_male_q2=summary.entitlement_amount_male_q2,
                entitlement_amount_male_q3=summary.entitlement_amount_male_q3,
                entitlement_amount_female_q1=summary.entitlement_amount_female_q1,
                entitlement_amount_female_q2=summary.entitlement_amount_female_q2,
                entitlement_amount_female_q3=summary.entitlement_amount_female_q3,
            ),
        )

    @staticmethod
    def _fmt_age(value, units):
        return f"{value} {units}" if value is not None else None

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
        if target_registry != "individual":
            raise ValueError("Only individual registry supported")

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        result = await bg_task_session.execute(
            select(BeneficiaryListDetails.registrant_details).where(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
            )
        )

        registrant_ids: List[int] = []
        for details in result.scalars().all():
            if isinstance(details, list):
                for r in details:
                    try:
                        registrant_ids.append(int(r["registrant_id"]))
                    except (KeyError, TypeError, ValueError):
                        continue
            elif isinstance(details, dict):
                try:
                    registrant_ids.append(int(details["registrant_id"]))
                except (KeyError, TypeError, ValueError):
                    pass
        
        registrant_ids = list(set(registrant_ids))

        if not registrant_ids:
            return BeneficiarySearchResponsePayload(
                total_beneficiary_count=0,
                page=page,
                page_size=page_size,
                beneficiaries=[],
            )

        query, params = self.construct_beneficiary_search_sql_query(
            registrant_ids, search_query, order_by, page_size, page
        )

        rows = (await sr_session.execute(query, params)).mappings().all()

        total_count = await self._get_total_beneficiary_count(
            sr_session, registrant_ids, search_query
        )

        beneficiaries = [
            G2PIndividualRegistryPayload(
                id=row["id"],
                link_registry_id=row["registrant_id_str"],
                name=row["name"],
                gender=row["gender"],
                birthdate=row["birthdate"],
                region_name=row["region_name"],
                district_name=row["district_name"],
                benf_zan_id=row["benf_zan_id"],
                nominee_first_name=row["nominee_first_name"],
                nominee_gender=row["nominee_gender"],
                nominee_zanid=row["nominee_zanid"],
                nominee_region=row["nominee_region"],
                nominee_district=row["nominee_district"],
            )
            for row in rows
        ]

        return BeneficiarySearchResponsePayload(
            total_beneficiary_count=total_count,
            page=page,
            page_size=page_size,
            beneficiaries=beneficiaries,
        )

    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        registrant_ids: List[int],
        search_query: Optional[str],
    ) -> int:
        if not registrant_ids:
            return 0

        query, params = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, search_query
        )

        if query is None:
            return 0

        return (await sr_session.execute(query, params)).scalar_one()

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
        registrant_ids: Set[int] = {
            int(RegistrantDetails(**r).registrant_id)
            for d in beneficiary_list_details
            for r in d.registrant_details
        }

        registrants = self.get_registrants_by_ids(list(registrant_ids), sr_session)

        ages = [
            self.calculate_age(r.birthdate)
            for r in registrants
            if r.birthdate
        ]

        summary = BeneficiaryListSummaryIndividualModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        if ages:
            a = np.array(ages)
            summary.age_q1 = round(float(np.percentile(a, 25, method="midpoint")), 2)
            summary.age_q2 = round(float(np.percentile(a, 50, method="midpoint")), 2)
            summary.age_q3 = round(float(np.percentile(a, 75, method="midpoint")), 2)
            summary.age_mean = round(float(np.mean(a)), 2)

        bg_task_session.add(summary)

    def get_registrants_by_ids(
        self, registrant_ids: List[int], sr_session: Session
    ) -> List[G2PIndividualRegistry]:
        if not registrant_ids:
            return []

        return list(
            sr_session.query(G2PIndividualRegistry)
            .filter(G2PIndividualRegistry.id.in_(registrant_ids))
            .yield_per(500)
        )

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registrant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        """
        SECURITY NOTE:
        This method executes TRUSTED INTERNAL SQL ONLY.
        Callers must never pass user-provided input.
        """
        sql_query_with_registrant_id = (
            self.construct_get_is_registrant_entitled_sql_query(
                registrant_id, sql_query
            )
        )
        return sr_session.execute(sql_query_with_registrant_id).fetchone() is not None

    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        """
        Alias for get_is_registrant_entitled to handle typo in celery worker.
        """
        return self.get_is_registrant_entitled(registrant_id, sql_query, sr_session)

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        ALLOWED_MULTIPLIERS = {
            "household_size",
            "disability_multiplier",
            "elderly_multiplier",
        }
        if multiplier not in ALLOWED_MULTIPLIERS:
            raise ValueError(f"Invalid multiplier column: {multiplier}")

        sql_query = self.construct_multiplier_sql_query(
            multiplier, target_registry="individual"
        )
        if sql_query is None:
            return 1

        result = sr_session.execute(
            sql_query, {"registrant_id": registrant_id}
        ).fetchone()

        return int(result[0]) if result and result[0] is not None else 1

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        registrant_ids = {
            int(RegistrantDetails(**r).registrant_id)
            for d in details
            for r in d.registrant_details
        }

        registrants = self.get_registrants_by_ids(list(registrant_ids), sr_session)
        registry_map = {r.id: r for r in registrants}

        entitlements: Dict[int, List[float]] = {}
        male: Dict[int, List[float]] = {}
        female: Dict[int, List[float]] = {}

        for d in details:
            for r in d.registrant_details:
                rd = RegistrantDetails(**r)
                reg = registry_map.get(int(rd.registrant_id))
                gender = reg.gender if reg else None

                for code, value in rd.entitlement.items():
                    entitlements.setdefault(code, []).append(value)
                    if gender == Gender.MALE.value:
                        male.setdefault(code, []).append(value)
                    elif gender == Gender.FEMALE.value:
                        female.setdefault(code, []).append(value)

        stats = self.compute_stats_dict(entitlements)
        male_stats = self.compute_stats_dict(male)
        female_stats = self.compute_stats_dict(female)

        bg_task_session.execute(
            update(BeneficiaryListSummaryIndividualModel)
            .where(
                BeneficiaryListSummaryIndividualModel.beneficiary_list_id
                == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(stats["total"]),
                average_entitlement_per_person=dict(stats["average"]),
                entitlement_amount_q1=dict(stats["q1"]),
                entitlement_amount_q2=dict(stats["q2"]),
                entitlement_amount_q3=dict(stats["q3"]),
                average_entitlement_male=dict(male_stats["average"]),
                entitlement_amount_male_q1=dict(male_stats["q1"]),
                entitlement_amount_male_q2=dict(male_stats["q2"]),
                entitlement_amount_male_q3=dict(male_stats["q3"]),
                average_entitlement_female=dict(female_stats["average"]),
                entitlement_amount_female_q1=dict(female_stats["q1"]),
                entitlement_amount_female_q2=dict(female_stats["q2"]),
                entitlement_amount_female_q3=dict(female_stats["q3"]),
            )
        )

    # ===============================
    # SQL Construction Overrides
    # ===============================
    def construct_beneficiary_search_sql_query(
        self,
        registrant_ids: List[int],
        search_query: Optional[str],
        order_by: str,
        page_size: int,
        page: int,
    ) -> Tuple[TextClause, Dict[str, Any]]:
        ALLOWED_ORDER_BY = {
            "id asc": "res_partner.id ASC",
            "id desc": "res_partner.id DESC",
            "name asc": "res_partner.name ASC",
            "name desc": "res_partner.name DESC",
        }
        key = order_by.lower() if isinstance(order_by, str) else "id asc"
        order_sql = ALLOWED_ORDER_BY.get(key, "id ASC")

        where = ""
        params: Dict[str, Any] = {}

        if search_query and search_query != "[]":
            search_query = search_query.replace("“", '"').replace("”", '"')
            search_query = search_query.replace("‘", "'").replace("’", "'")
            if any(k in search_query.upper() for k in ["RES_PARTNER", '"', "'", "="]):
                where = f"AND ({search_query})"
            else:
                where = "AND name ILIKE :search_query"
                params["search_query"] = f"%{search_query}%"

        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )
        for i, rid in enumerate(registrant_ids):
            params[f"registrant_id_{i}"] = rid

        query = text(
            f"""
            SELECT res_partner.id, res_partner.name, res_partner.gender, res_partner.birthdate, res_partner.id::TEXT AS registrant_id_str, 
                   r.name AS region_name, d.name AS district_name,
                   res_partner.benf_zan_id, res_partner.nominee_first_name, res_partner.nominee_gender, 
                   res_partner.nominee_zanid, res_partner.nominee_region, res_partner.nominee_district
            FROM res_partner
            LEFT JOIN g2p_region r ON res_partner.region = r.id
            LEFT JOIN g2p_district d ON res_partner.district = d.id
            WHERE res_partner.id IN ({registrant_placeholders}) {where}
            ORDER BY {order_sql}
            OFFSET :offset LIMIT :limit
            """
        )

        params.update(
            {
                "offset": page_size * (page - 1),
                "limit": page_size,
            }
        )

        return query, params

    def construct_beneficiary_search_count_sql_query(
        self,
        registrant_ids: List[int],
        search_query: Optional[str],
    ) -> Tuple[TextClause, Dict[str, Any]]:
        where = ""
        params: Dict[str, Any] = {}

        if search_query and search_query != "[]":
            search_query = search_query.replace("“", '"').replace("”", '"')
            search_query = search_query.replace("‘", "'").replace("’", "'")
            if any(k in search_query.upper() for k in ["RES_PARTNER", '"', "'", "="]):
                where = f"AND ({search_query})"
            else:
                where = "AND name ILIKE :search_query"
                params["search_query"] = f"%{search_query}%"

        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )
        for i, rid in enumerate(registrant_ids):
            params[f"registrant_id_{i}"] = rid

        query = text(
            f"""
            SELECT COUNT(*)
            FROM res_partner
            WHERE id IN ({registrant_placeholders}) {where}
            """
        )

        return query, params

    def construct_multiplier_sql_query(
        self, multiplier: str, target_registry: str
    ) -> Optional[TextClause]:
        if not multiplier or multiplier == "none":
            return None

        # Safe: multiplier is validated against a strict allowlist
        return text(
            f"""
            SELECT {multiplier}::TEXT
            FROM res_partner
            WHERE id = :registrant_id
            """
        )

    def construct_get_is_registrant_entitled_sql_query(
        self, registrant_id: str, sql_query: str
    ) -> TextClause:
        sql = sql_query.strip().upper()
        forbidden = {";", "DROP", "DELETE", "UPDATE", "INSERT"}

        if not sql.startswith("SELECT") or any(k in sql for k in forbidden):
            raise ValueError("Unsafe SQL detected")

        if "RES_PARTNER" not in sql:
            raise ValueError("Query must target res_partner only")

        clause = "AND" if "WHERE" in sql else "WHERE"
        final_sql = f"{sql_query} {clause} res_partner.id = :registrant_id"

        return text(final_sql).params(registrant_id=registrant_id)
