import logging
from datetime import date
from typing import Dict, List, Optional

import numpy as np
from fastapi_cache.decorator import cache
from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    RegistrantDetails,
)
from openg2p_pbms_models.models import Gender
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from ..cache import beneficiary_count_key_builder
from ..interface import RegistryInterface
from ..models import (
    BeneficiaryListSummaryStudent as BeneficiaryListSummaryStudentModel,
    G2PStudentRegistry,
)
from ..schema import (
    BeneficiaryListSummary,
    BeneficiaryListSummaryStudent,
    BeneficiaryListSummaryStudentPayload,
    G2PStudentRegistryPayload,
)

_logger = logging.getLogger("openg2p_bg_task_registry_adapters")


class RegistryStudent(RegistryInterface):
    """Fetches student data and computes summary statistics"""

    # ===================
    # Summary API Methods
    # ===================
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryStudentPayload:
        _logger.info(f"Fetching summary for beneficiary_list_id: {beneficiary_list_id}")
        beneficiary_list_summary_student = await bg_task_session.execute(
            select(BeneficiaryListSummaryStudentModel).where(
                BeneficiaryListSummaryStudentModel.beneficiary_list_id == beneficiary_list_id
            )
        )
        beneficiary_list_summary_student = beneficiary_list_summary_student.scalars().first()

        if not beneficiary_list_summary_student:
            raise ValueError(
                f"No summary found for beneficiary_list_id: {beneficiary_list_id}"
            )

        summary_student_payload = BeneficiaryListSummaryStudentPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_student.id,
                program_id=beneficiary_list_summary_student.program_id,
                program_mnemonic=beneficiary_list_summary_student.program_mnemonic,
                target_registry=beneficiary_list_summary_student.target_registry,
                beneficiary_list_id=beneficiary_list_summary_student.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_student.number_of_registrants,
                date_created=beneficiary_list_summary_student.date_created,
                total_disbursement_quantity=beneficiary_list_summary_student.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_student.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryStudent(
                age_mean=f"{beneficiary_list_summary_student.age_mean} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_mean is not None
                else None,
                age_q1=f"{beneficiary_list_summary_student.age_q1} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q1 is not None
                else None,
                age_q2=f"{beneficiary_list_summary_student.age_q2} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q2 is not None
                else None,
                age_q3=f"{beneficiary_list_summary_student.age_q3} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q3 is not None
                else None,
                average_entitlement_female=beneficiary_list_summary_student.average_entitlement_female,
                average_entitlement_male=beneficiary_list_summary_student.average_entitlement_male,
                entitlement_amount_q1=beneficiary_list_summary_student.entitlement_amount_q1,
                entitlement_amount_q2=beneficiary_list_summary_student.entitlement_amount_q2,
                entitlement_amount_q3=beneficiary_list_summary_student.entitlement_amount_q3,
                entitlement_amount_male_q1=beneficiary_list_summary_student.entitlement_amount_male_q1,
                entitlement_amount_male_q2=beneficiary_list_summary_student.entitlement_amount_male_q2,
                entitlement_amount_male_q3=beneficiary_list_summary_student.entitlement_amount_male_q3,
                entitlement_amount_female_q1=beneficiary_list_summary_student.entitlement_amount_female_q1,
                entitlement_amount_female_q2=beneficiary_list_summary_student.entitlement_amount_female_q2,
                entitlement_amount_female_q3=beneficiary_list_summary_student.entitlement_amount_female_q3,
            ),
        )
        return summary_student_payload

    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryStudentPayload:
        beneficiary_list_summary_student = (
            bg_task_session.query(BeneficiaryListSummaryStudentModel)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .first()
        )

        if not beneficiary_list_summary_student:
            raise ValueError(
                f"No summary found for beneficiary_list_id: {beneficiary_list_id}"
            )

        summary_student_payload = BeneficiaryListSummaryStudentPayload(
            beneficiary_list_summary=BeneficiaryListSummary(
                id=beneficiary_list_summary_student.id,
                program_id=beneficiary_list_summary_student.program_id,
                program_mnemonic=beneficiary_list_summary_student.program_mnemonic,
                target_registry=beneficiary_list_summary_student.target_registry,
                beneficiary_list_id=beneficiary_list_summary_student.beneficiary_list_id,
                number_of_registrants=beneficiary_list_summary_student.number_of_registrants,
                date_created=beneficiary_list_summary_student.date_created,
                total_disbursement_quantity=beneficiary_list_summary_student.total_disbursement_quantity,
                average_entitlement_per_registrant=beneficiary_list_summary_student.average_entitlement_per_person,
            ),
            registry_summary=BeneficiaryListSummaryStudent(
                age_mean=f"{beneficiary_list_summary_student.age_mean} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_mean is not None
                else None,
                age_q1=f"{beneficiary_list_summary_student.age_q1} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q1 is not None
                else None,
                age_q2=f"{beneficiary_list_summary_student.age_q2} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q2 is not None
                else None,
                age_q3=f"{beneficiary_list_summary_student.age_q3} {beneficiary_list_summary_student.age_units}"
                if beneficiary_list_summary_student.age_q3 is not None
                else None,
                average_entitlement_female=beneficiary_list_summary_student.average_entitlement_female,
                average_entitlement_male=beneficiary_list_summary_student.average_entitlement_male,
                entitlement_amount_q1=beneficiary_list_summary_student.entitlement_amount_q1,
                entitlement_amount_q2=beneficiary_list_summary_student.entitlement_amount_q2,
                entitlement_amount_q3=beneficiary_list_summary_student.entitlement_amount_q3,
                entitlement_amount_male_q1=beneficiary_list_summary_student.entitlement_amount_male_q1,
                entitlement_amount_male_q2=beneficiary_list_summary_student.entitlement_amount_male_q2,
                entitlement_amount_male_q3=beneficiary_list_summary_student.entitlement_amount_male_q3,
                entitlement_amount_female_q1=beneficiary_list_summary_student.entitlement_amount_female_q1,
                entitlement_amount_female_q2=beneficiary_list_summary_student.entitlement_amount_female_q2,
                entitlement_amount_female_q3=beneficiary_list_summary_student.entitlement_amount_female_q3,
            ),
        )

        return summary_student_payload

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
        registrant_details = await bg_task_session.execute(
            select(BeneficiaryListDetails.registrant_details).where(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list_id
            )
        )
        registrant_details = registrant_details.scalars().all()
        registrant_ids = []
        for registrant_detail in registrant_details:
            for registrant in registrant_detail:
                registrant_ids.append(registrant["registrant_id"])

        student_search_query, student_search_params = self.construct_beneficiary_search_sql_query(
            registrant_ids,
            target_registry,
            search_query,
            order_by,
            page_size,
            page,
        )
        student_search_results = (
            (await sr_session.execute(student_search_query, student_search_params))
            .mappings()
            .all()
        )

        total_beneficiary_count = await self._get_total_beneficiary_count(
            sr_session, beneficiary_list_id, registrant_ids, search_query
        )

        beneficiaries = []
        if student_search_results:
            beneficiaries = [
                G2PStudentRegistryPayload(
                    id=student["id"],
                    link_registry_id=student["link_registry_id"],
                    name=student["name"],
                    gender=student["gender"],
                    institution_name=student["institution_name"],
                    date_of_birth=student["date_of_birth"],
                    small_area_code=student["small_area_code"],
                    large_area_code=student["large_area_code"],
                )
                for student in student_search_results
            ]

        response_payload = BeneficiarySearchResponsePayload(
            total_beneficiary_count=total_beneficiary_count,
            page=page,
            page_size=page_size,
            beneficiaries=beneficiaries,
        )

        return response_payload

    @cache(expire=120, key_builder=beneficiary_count_key_builder)
    async def _get_total_beneficiary_count(
        self,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        search_query: Optional[str] = None,
    ) -> int:
        beneficiary_count_query, beneficiary_count_params = self.construct_beneficiary_search_count_sql_query(
            registrant_ids, "student", search_query
        )
        total_beneficiary_count = (
            await sr_session.execute(beneficiary_count_query, beneficiary_count_params)
        ).scalar_one()

        return total_beneficiary_count

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
        ages = []
        for beneficiary_list_detail in beneficiary_list_details:
            registrant_ids = []
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant_ids.append(registrant_detail.registrant_id)

            registrants = self.get_registrants_by_ids(registrant_ids, sr_session)
            for registrant in registrants:
                if registrant.date_of_birth:
                    ages.append(self.calculate_age(registrant.date_of_birth))

        student_summary = BeneficiaryListSummaryStudentModel(
            program_id=base_summary.program_id,
            program_mnemonic=base_summary.program_mnemonic,
            target_registry=base_summary.target_registry,
            beneficiary_list_id=base_summary.beneficiary_list_id,
            number_of_registrants=base_summary.number_of_registrants,
            date_created=base_summary.date_created,
        )

        if ages:
            ages_array = np.array(ages)
            student_summary.age_q1 = round(float(np.percentile(ages_array, 25, method="midpoint")), 2)
            student_summary.age_q2 = round(float(np.percentile(ages_array, 50, method="midpoint")), 2)
            student_summary.age_q3 = round(float(np.percentile(ages_array, 75, method="midpoint")), 2)
            student_summary.age_mean = round(float(np.mean(ages_array)), 2)

        bg_task_session.add(student_summary)

    def get_registrants_by_ids(
        self, registrant_ids, sr_session
    ) -> List[G2PStudentRegistry]:
        students = sr_session.query(G2PStudentRegistry).filter(
            G2PStudentRegistry.link_registry_id.in_(registrant_ids)
        )

        return list(students.yield_per(500))

    @staticmethod
    def calculate_age(birth_date) -> int:
        today = date.today()
        return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

    # =================================
    # Entitlement Celery Worker Methods
    # =================================
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        sql_query_with_registrant_id = self.construct_get_is_registrant_entitled_sql_query(
            registrant_id, "student", sql_query
        )
        result = sr_session.execute(sql_query_with_registrant_id).fetchone()
        return result is not None

    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        if not multiplier or multiplier == "none":
            return 1

        sql_query = self.construct_multiplier_sql_query(
            multiplier, target_registry="student"
        )
        params = {"registrant_id": registrant_id}
        result = sr_session.execute(sql_query, params).fetchone()
        multiplier_value: int = (
            int(result[0]) if result and result[0] is not None else 1
        )

        return multiplier_value

    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        beneficiary_list_details = (
            bg_task_session.query(BeneficiaryListDetails)
            .filter_by(beneficiary_list_id=beneficiary_list_id)
            .all()
        )

        registrant_map_from_registry: Dict[str, G2PStudentRegistry] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            registrant_ids = []
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant_ids.append(registrant_detail.registrant_id)

            registrants_list: List[G2PStudentRegistry] = self.get_registrants_by_ids(
                registrant_ids, sr_session
            )

            for registrant in registrants_list:
                registrant_map_from_registry[str(registrant.link_registry_id)] = registrant

        # Collect entitlements per benefit_code_id
        entitlements: Dict[int, List[float]] = {}
        entitlements_male: Dict[int, List[float]] = {}
        entitlements_female: Dict[int, List[float]] = {}

        for beneficiary_list_detail in beneficiary_list_details:
            for registrant_detail in beneficiary_list_detail.registrant_details:
                registrant_detail = RegistrantDetails(**registrant_detail)
                registrant = registrant_map_from_registry.get(
                    str(registrant_detail.registrant_id)
                )
                gender = registrant.gender if registrant else None

                for benefit_code_id, value in registrant_detail.entitlement.items():
                    entitlements.setdefault(benefit_code_id, []).append(value)
                    if gender == Gender.MALE.value:
                        entitlements_male.setdefault(benefit_code_id, []).append(value)
                    elif gender == Gender.FEMALE.value:
                        entitlements_female.setdefault(benefit_code_id, []).append(value)
                    else:
                        raise ValueError(f"Invalid gender: {gender}")

        entitlement_stats = self.compute_stats_dict(entitlements)
        entitlement_male_stats = self.compute_stats_dict(entitlements_male)
        entitlement_female_stats = self.compute_stats_dict(entitlements_female)

        bg_task_session.execute(
            update(BeneficiaryListSummaryStudentModel)
            .where(
                BeneficiaryListSummaryStudentModel.beneficiary_list_id == beneficiary_list_id
            )
            .values(
                total_disbursement_quantity=dict(entitlement_stats["total"]),
                average_entitlement_per_person=dict(entitlement_stats["average"]),
                entitlement_amount_q1=dict(entitlement_stats["q1"]),
                entitlement_amount_q2=dict(entitlement_stats["q2"]),
                entitlement_amount_q3=dict(entitlement_stats["q3"]),
                average_entitlement_male=dict(entitlement_male_stats["average"]),
                entitlement_amount_male_q1=dict(entitlement_male_stats["q1"]),
                entitlement_amount_male_q2=dict(entitlement_male_stats["q2"]),
                entitlement_amount_male_q3=dict(entitlement_male_stats["q3"]),
                average_entitlement_female=dict(entitlement_female_stats["average"]),
                entitlement_amount_female_q1=dict(entitlement_female_stats["q1"]),
                entitlement_amount_female_q2=dict(entitlement_female_stats["q2"]),
                entitlement_amount_female_q3=dict(entitlement_female_stats["q3"]),
            )
        )

    def compute_stats_dict(self, entitlements_dict: Dict[int, List[float]]) -> dict:
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
