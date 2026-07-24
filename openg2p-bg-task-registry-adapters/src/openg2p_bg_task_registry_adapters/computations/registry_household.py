import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..interface import RegistryInterface

_logger = logging.getLogger("openg2p_bg_task_registry_adapters")


class RegistryHousehold(RegistryInterface):
    """Fetches household data and computes summary statistics"""

    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ):
        _logger.info(f"Fetching summary for household beneficiary_list_id: {beneficiary_list_id}")
        return None
