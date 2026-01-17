from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..computations import (
    RegistryIndividual,
)
from ..interface import RegistryInterface
from ..models import G2PRegistryType


class RegistryFactory:
    """Get the appropriate summary computation class based on the registrant type"""

    @staticmethod
    def get_registry_class(
        target_registry,
    ) -> RegistryInterface:
        if target_registry == G2PRegistryType.INDIVIDUAL.value:
            return RegistryIndividual()

        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
