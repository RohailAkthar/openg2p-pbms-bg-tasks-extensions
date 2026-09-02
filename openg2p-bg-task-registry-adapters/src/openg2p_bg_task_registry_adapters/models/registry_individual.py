from .base_registry import G2PRegistry
from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class G2PRegisterIndividual(G2PRegistry):
    __tablename__ = "g2p_register_individuals"

    # Functional ID & Links
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    record_image_document_id: Mapped[str] = mapped_column(Text, nullable=True)
    search_text: Mapped[str] = mapped_column(Text, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
    record_status_reason: Mapped[str] = mapped_column(String, nullable=True)

    # Foundational ID
    foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    foundational_id_masked: Mapped[str] = mapped_column(String, nullable=True)
    foundational_id_verification_status: Mapped[str] = mapped_column(String, nullable=True)
    identity_evidence_type: Mapped[str] = mapped_column(String, nullable=True)

    # Names & Demographics
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    given_name: Mapped[str] = mapped_column(String, nullable=True)
    prefix: Mapped[str] = mapped_column(String, nullable=True)
    suffix: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)
    estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)
    age_method: Mapped[str] = mapped_column(String, nullable=True)
    citizenship_category: Mapped[str] = mapped_column(String, nullable=True)
    marital_status: Mapped[str] = mapped_column(String, nullable=True)

    # Contact & Household Relations
    preferred_contact_method: Mapped[str] = mapped_column(String, nullable=True)
    contact_person_name: Mapped[str] = mapped_column(String, nullable=True)
    relationship_to_head: Mapped[str] = mapped_column(String, nullable=True)
    residency_status: Mapped[str] = mapped_column(String, nullable=True)
    dependency_indicator: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Location
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    altitude: Mapped[str] = mapped_column(String, nullable=True)
    plus_code: Mapped[str] = mapped_column(String, nullable=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    address_line_2: Mapped[str] = mapped_column(String, nullable=True)
    postal_code: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    geo_lowest_level_value_id: Mapped[str] = mapped_column(String, nullable=True)

    # Vulnerability & Social Protection
    disability_status: Mapped[str] = mapped_column(String, nullable=True)
    plw_status: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    plw_status_date: Mapped[Date] = mapped_column(Date, nullable=True)
    orphanhood_flag: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    chronic_illness_flag: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    displacement_status: Mapped[str] = mapped_column(String, nullable=True)
    pastoralist_classification: Mapped[str] = mapped_column(String, nullable=True)
    high_mobility_indicator: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Livelihood & Economics
    primary_livelihood: Mapped[str] = mapped_column(String, nullable=True)
    secondary_livelihood: Mapped[str] = mapped_column(String, nullable=True)
    occupation: Mapped[str] = mapped_column(String, nullable=True)
    income_level: Mapped[str] = mapped_column(String, nullable=True)
    employment_status: Mapped[str] = mapped_column(String, nullable=True)
    education_level: Mapped[str] = mapped_column(String, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)
    registration_date: Mapped[Date] = mapped_column(Date, nullable=True)
    coping_strategies_index: Mapped[int] = mapped_column(Integer, nullable=True)
