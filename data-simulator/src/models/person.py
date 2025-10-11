"""Person class for representing individual family members."""

import uuid
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .location import Location


class Gender(Enum):
    """Enumeration for person gender."""

    MALE = "male"
    FEMALE = "female"


class SocialCategory(Enum):
    """Enumeration for person's social/professional category."""

    FARMERS = "farmers"  # Agriculteurs exploitants
    ARTISANS_MERCHANTS_ENTREPRENEURS = (
        "artisans_merchants_entrepreneurs"  # Artisans, commerçants, chefs d'entreprise
    )
    EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS = "executives_higher_intellectual_professions"  # Cadres et professions intellectuelles supérieures
    INTERMEDIATE_PROFESSIONS = "intermediate_professions"  # Professions intermédiaires
    EMPLOYEES = "employees"  # Employés
    WORKERS = "workers"  # Ouvriers
    RETIREES = "retirees"  # Retraités
    INACTIVE = "inactive"  # Autres personnes sans activité professionnelle


class Religiosity(Enum):
    """Enumeration for family's religiosity level."""

    VERY_RELIGIOUS = "very_religious"
    MODERATE_RELIGIOUS = "moderate_religious"
    OCCASIONAL_RELIGIOUS = "occasional_religious"
    NO_RELIGION = "no_religion"


class Person:
    """Represents a person with unique identifier, gender, age, social category, and assigned locations."""

    def __init__(
        self,
        gender: Gender,
        age: int,
        social_category: SocialCategory,
        person_id: Optional[str] = None,
        school_location: Optional["Location"] = None,
        work_location: Optional["Location"] = None,
        family=None,
    ):
        """
        Initialize a Person instance.
        Args:
            gender: Gender of the person (Gender enum)
            age: Age of the person in years
            social_category: Social/professional category (SocialCategory enum)
            person_id: Optional unique identifier. If not provided, a UUID will be generated.
            school_location: School location (Location object)
            work_location: Work location (Location object)
            family: Reference to the family object
        """
        self.person_id = person_id or str(uuid.uuid4())
        self.gender = gender
        self.age = age
        self.social_category = social_category
        self.school_location = school_location
        self.work_location = work_location
        self.family = family
