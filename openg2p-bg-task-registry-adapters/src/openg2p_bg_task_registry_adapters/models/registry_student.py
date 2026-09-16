from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String
from sqlalchemy.orm import mapped_column


class G2PStudentRegistry(G2PRegistry):
    __tablename__ = "g2p_register_students"

    record_name = mapped_column(String, nullable=True)
    functional_record_id = mapped_column(String, nullable=True)
    udise_student_id = mapped_column(String, nullable=True)
    student_id = mapped_column(String, nullable=True)
    first_name = mapped_column(String, nullable=True)
    last_name = mapped_column(String, nullable=True)
    gender = mapped_column(String, nullable=True)
    school_name = mapped_column(String, nullable=True)
    class_grade = mapped_column(String, nullable=True)
    birth_date = mapped_column(Date, nullable=True)
    district = mapped_column(String, nullable=True)
    block = mapped_column(String, nullable=True)
    village = mapped_column(String, nullable=True)

    @property
    def display_student_id(self):
        return self.udise_student_id or self.student_id or self.functional_record_id or self.internal_record_id

    @property
    def name(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        if not name and self.record_name:
            if "(" in self.record_name and self.record_name.endswith(")"):
                name = self.record_name[: self.record_name.rfind("(")].strip()
            else:
                name = self.record_name
        return name or self.record_name

    @property
    def institution_name(self):
        return self.school_name

    @property
    def date_of_birth(self):
        return self.birth_date

