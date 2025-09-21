"""Person class for representing individual family members."""

import uuid
from enum import Enum
from typing import Optional


class Gender(Enum):
    """Enumeration for person gender."""
    MALE = "male"
    FEMALE = "female"


class SocialCategory(Enum):
    """Enumeration for person's social/professional category."""
    FARMERS = "farmers"  # Agriculteurs exploitants
    ARTISANS_MERCHANTS_ENTREPRENEURS = "artisans_merchants_entrepreneurs"  # Artisans, commerçants, chefs d'entreprise
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
    """Represents a person with unique identifier, gender, age, and social category."""
    
    def __init__(self, gender: Gender, age: int, social_category: SocialCategory, person_id: Optional[str] = None):
        """
        Initialize a Person instance.
        
        Args:
            gender: Gender of the person (Gender enum)
            age: Age of the person in years
            social_category: Social/professional category (SocialCategory enum)
            person_id: Optional person identifier. If not provided, a UUID will be generated.
        """
        self.person_id = person_id or str(uuid.uuid4())
        self.gender = gender
        self.age = age
        self.social_category = social_category
    
    def __str__(self) -> str:
        """Return string representation of the person."""
        return f"Person(id={self.person_id[:8]}..., {self.gender.value}, age={self.age}, {self.social_category.value})"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the person."""
        return f"Person(person_id='{self.person_id}', gender={self.gender}, age={self.age}, social_category={self.social_category})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on person_id."""
        if not isinstance(other, Person):
            return False
        return self.person_id == other.person_id
    
    def __hash__(self) -> int:
        """Return hash based on person_id."""
        return hash(self.person_id)
    
    @property
    def is_adult(self) -> bool:
        """Return True if person is an adult (18 or older)."""
        return self.age >= 18
    
    @property
    def is_child(self) -> bool:
        """Return True if person is a child (under 18)."""
        return self.age < 18