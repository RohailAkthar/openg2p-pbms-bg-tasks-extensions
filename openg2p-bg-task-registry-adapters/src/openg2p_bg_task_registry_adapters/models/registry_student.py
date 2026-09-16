from openg2p_pbms_models.models import G2PRegistry
from sqlalchemy import Date, String
from sqlalchemy.orm import mapped_column


class G2PStudentRegistry(G2PRegistry):
    __tablename__ = "g2p_register_students"

    record_name = mapped_column(String, nullable=True)
    student_id = mapped_column(String, nullable=True)
    gender = mapped_column(String, nullable=True)
    school_name = mapped_column(String, nullable=True)
    class_grade = mapped_column(String, nullable=True)
    birth_date = mapped_column(Date, nullable=True)
    district = mapped_column(String, nullable=True)
    block = mapped_column(String, nullable=True)
    village = mapped_column(String, nullable=True)

    @property
    def name(self):
        return self.record_name

    @property
    def institution_name(self):
        return self.school_name

    @property
    def date_of_birth(self):
        return self.birth_date

