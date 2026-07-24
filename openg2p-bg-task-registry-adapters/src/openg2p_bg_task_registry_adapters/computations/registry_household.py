import logging
from typing import Any, Dict, List, Optional, Tuple

from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..interface import RegistryInterface

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
    ):
        _logger.info(f"Fetching summary for household beneficiary_list_id: {beneficiary_list_id}")
        return None

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ):
        _logger.info(f"Fetching sync summary for household beneficiary_list_id: {beneficiary_list_id}")
        return None

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
        order_by: str = "id asc",
    ) -> BeneficiarySearchResponsePayload:
        _logger.info(f"Searching household beneficiaries for list id: {beneficiary_list_id}")
        return BeneficiarySearchResponsePayload(
            total_beneficiary_count=0,
            page=page,
            page_size=page_size,
            beneficiaries=[],
        )
