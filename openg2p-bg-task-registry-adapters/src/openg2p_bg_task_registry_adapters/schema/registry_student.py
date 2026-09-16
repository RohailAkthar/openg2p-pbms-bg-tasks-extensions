from datetime import date, datetime
from typing import Optional

from .registry import G2PRegistryPayload


class G2PStudentRegistryPayload(G2PRegistryPayload):
    name: Optional[str] = None
    student_id: Optional[str] = None
    gender: Optional[str] = None
    school_name: Optional[str] = None
    institution_name: Optional[str] = None
    class_grade: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
    date_of_birth: Optional[date] = None
