from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Tuple

import numpy as np

from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    Disbursement,
)
from openg2p_pbms_models.models import G2PRegistry
from openg2p_bg_task_models.models import BeneficiaryListDetails
from sqlalchemy import TextClause, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..schema import BeneficiaryListSummaryPayload


class RegistryInterface(ABC):
    """
    Base class for Registry Interface
    Defines methods for interacting with the registry classes
    """

    # ================
    # Summary methods
    # ================
    @abstractmethod
    async def get_summary(
        self, beneficiary_list_id: str, bg_task_session: AsyncSession, formated: bool = False
    ) -> BeneficiaryListSummaryPayload:
        """
        Abstract method to get async summary statistics for a given beneficiary_list_id.
        """
        raise NotImplementedError("Subclasses must implement get_summary()")

    @abstractmethod
    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryPayload:
        """
        Abstract method to get synchronous summary statistics for a given beneficiary_list_id.
        """
        raise NotImplementedError("Subclasses must implement get_summary_sync()")

    @abstractmethod
    def compute_eligibility_statistics(
        self,
        beneficiary_list_details: List[BeneficiaryListDetails],
        base_summary,
        sr_session: Session,
        bg_task_session: Session,
    ):
        """
        Abstract method to compute eligibility summary statistics and update the summary table.
        """
        raise NotImplementedError("Subclasses must implement compute_eligibility_statistics()")

    @abstractmethod
    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        """
        Abstract method to compute entitlement statistics and update relevant summary fields.
        """
        raise NotImplementedError(
            "Subclasses must implement compute_entitlement_statistics()"
        )

    # =================
    # Registry methods
    # =================
    @abstractmethod
    def get_registrants_by_ids(
        self, registrant_ids: List, sr_session: Session
    ) -> List[G2PRegistry]:
        """
        Abstract method to fetch registrants for given registrant_ids from the registry database.
        """
        raise NotImplementedError("Subclasses must implement get_registrants_by_ids()")

    @abstractmethod
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        """
        Abstract method to check if a registrant is entitled based on custom SQL and session.
        """
        raise NotImplementedError(
            "Subclasses must implement get_is_registant_entitled()"
        )

    @abstractmethod
    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        """
        Abstract method to get the multiplier value for entitlement calculation
        for a single registrant_id by executing a SQL query.
        """
        raise NotImplementedError(
            "Subclasses must implement get_entitlement_multiplier()"
        )

    @abstractmethod
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_query,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "id asc",
    ) -> BeneficiarySearchResponsePayload:
        """
        Abstract method to search beneficiaries for particular eligibility request id.
        """
        raise NotImplementedError("Subclasses must implement search_beneficiaries()")

    def get_bridge_disbursement_details(
        self,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        bg_task_session: Session,
    ) -> List[Disbursement]:
        raise NotImplementedError("Subclasses must implement get_bridge_disbursement_details()")

    # ===============================
    # Registry SQL Query Constructors
    # ===============================
    def construct_multiplier_sql_query(
        self, multiplier: str, target_registry: str
    ) -> TextClause:
        if not multiplier or multiplier == "none":
            return None

        table_name = f"g2p_{target_registry}_registry"
        sql_query = text(
            f"""
            SELECT {multiplier} FROM {table_name}
            WHERE link_registry_id = :registrant_id
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
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}

        # Replace curly quotes in the where clause
        where_clause = where_clause.replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")

        table_name = f"g2p_{target_registry}_registry"
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT * FROM {table_name}
            WHERE link_registry_id IN ({registrant_placeholders}) {where_clause_sql}
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
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}

        # Replace curly quotes in the where clause
        where_clause = where_clause.replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")

        table_name = f"g2p_{target_registry}_registry"
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE link_registry_id IN ({registrant_placeholders}) {where_clause_sql}
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

        if "WHERE" in sql_query.upper():
            sql_query += (
                f" AND g2p_{target_registry}_registry.link_registry_id = :registrant_id"
            )
        else:
            sql_query += (
                f" WHERE g2p_{target_registry}_registry.link_registry_id = :registrant_id"
            )

        params = {"registrant_id": registrant_id}

        return text(sql_query).params(**params)

    @staticmethod
    def calculate_age(birth_date) -> int:
        if not birth_date:
            return 0
        if isinstance(birth_date, str):
            birth_date = date.fromisoformat(birth_date)
        today = date.today()
        return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
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
