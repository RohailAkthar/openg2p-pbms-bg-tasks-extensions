from datetime import date, datetime
from typing import Optional

from .registry import G2PRegistryPayload


class G2PStudentRegistryPayload(G2PRegistryPayload):
    name: Optional[str] = None
    student_id: Optional[str] = None
    aadhaar_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    guardian_aadhaar: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    state: Optional[str] = None
    village: Optional[str] = None
    school_name: Optional[str] = None
    institution_name: Optional[str] = None
    school_udise_code: Optional[str] = None
    education_level: Optional[str] = None
    class_grade: Optional[str] = None
    admission_date: Optional[date] = None
    attendance_percentage: Optional[float] = None
    scholarship_status: Optional[str] = None
