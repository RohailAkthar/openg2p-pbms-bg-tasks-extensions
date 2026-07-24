from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..computations import (
    RegistryFarmer,
    RegistryStudent,
    RegistryHousehold,
)
from ..interface import RegistryInterface
from ..models import G2PRegistryType


class RegistryFactory:
    """Get the appropriate summary computation class based on the registrant type"""

    @staticmethod
    def get_registry_class(
        target_registry,
    ) -> RegistryInterface:
        if target_registry == G2PRegistryType.FARMER.value:
            return RegistryFarmer()

        elif target_registry == G2PRegistryType.STUDENT.value:
            return RegistryStudent()

        elif target_registry == G2PRegistryType.HOUSEHOLD.value:
            return RegistryHousehold()

        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
