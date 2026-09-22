from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..computations import RegisterFamilies, RegistryFarmer, RegistryStudent
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
        elif target_registry in (
            G2PRegistryType.GROUP.value,
            "families",
            "household",
            G2PRegistryType.GRAMSTACKHOUSEHOLD.value,
            "gramstackhousehold",
        ):
            return RegisterFamilies(target_registry=target_registry)
        else:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
