from .base_registry import G2PRegistry
from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class G2PRegisterHousehold(G2PRegistry):
    __tablename__ = "g2p_register_households"

    # Functional ID & Links
    functional_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    link_foundational_id: Mapped[str] = mapped_column(String, nullable=True)
    record_name: Mapped[str] = mapped_column(String, nullable=True)
    record_image_document_id: Mapped[str] = mapped_column(Text, nullable=True)
    search_text: Mapped[str] = mapped_column(Text, nullable=True)
    record_status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
    record_status_reason: Mapped[str] = mapped_column(String, nullable=True)

    # Location & Geo
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    altitude: Mapped[str] = mapped_column(String, nullable=True)
    plus_code: Mapped[str] = mapped_column(String, nullable=True)
    address_line_1: Mapped[str] = mapped_column(String, nullable=True)
    address_line_2: Mapped[str] = mapped_column(String, nullable=True)
    postal_code: Mapped[str] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=True)
    geo_lowest_level_value_id: Mapped[str] = mapped_column(String, nullable=True)

    # Headship
    household_head_internal_record_id: Mapped[str] = mapped_column(String, nullable=True)
    household_head_name: Mapped[str] = mapped_column(String, nullable=True)
    headship_type: Mapped[str] = mapped_column(String, nullable=True)
    husband_dead: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    husband_dead_date: Mapped[Date] = mapped_column(Date, nullable=True)

    # Demographics
    size_total: Mapped[int] = mapped_column(Integer, nullable=True)
    size_adults: Mapped[int] = mapped_column(Integer, nullable=True)
    size_children_u5: Mapped[int] = mapped_column(Integer, nullable=True)
    size_school_age: Mapped[int] = mapped_column(Integer, nullable=True)
    size_elderly: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_female_members: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_male_members: Mapped[int] = mapped_column(Integer, nullable=True)
    elderly_member_present: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Housing & Living Conditions
    dwelling_type: Mapped[str] = mapped_column(String, nullable=True)
    roof_material: Mapped[str] = mapped_column(String, nullable=True)
    wall_material: Mapped[str] = mapped_column(String, nullable=True)
    floor_material: Mapped[str] = mapped_column(String, nullable=True)
    tenure_status: Mapped[str] = mapped_column(String, nullable=True)
    rooms_count: Mapped[int] = mapped_column(Integer, nullable=True)
    overcrowding_indicator: Mapped[float] = mapped_column(Float, nullable=True)

    # Utilities & Extra Attributes
    water_source_type: Mapped[str] = mapped_column(String, nullable=True)
    water_distance_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    sanitation_type: Mapped[str] = mapped_column(String, nullable=True)
    lighting_source: Mapped[str] = mapped_column(String, nullable=True)
    cooking_fuel_type: Mapped[str] = mapped_column(String, nullable=True)
    mobile_phone_type: Mapped[str] = mapped_column(String, nullable=True)
    geo_code_hierarchy_json: Mapped[str] = mapped_column(Text, nullable=True)



