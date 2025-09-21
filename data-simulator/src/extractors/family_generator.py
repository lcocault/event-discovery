"""Family generation utilities with child distribution logic."""

import random
from typing import List
from models.family import Family
from models.person import Person, Gender, SocialCategory, Religiosity


class FamilyGenerator:
    """Generates families with specified child distribution."""
    
    def __init__(self):
        """Initialize the family generator with child distribution probabilities."""
        # Child distribution: 40% no children, 20% 1 child, 25% 2 children, 10% 3 children, 5% 4 children
        self.child_distribution = [
            (0, 0.40),  # 40% - no children
            (1, 0.20),  # 20% - 1 child
            (2, 0.25),  # 25% - 2 children
            (3, 0.10),  # 10% - 3 children
            (4, 0.05),  # 5% - 4 children
        ]
        
        # Religiosity distribution: 5% very religious, 10% moderate, 30% occasional, 55% no religion
        self.religiosity_distribution = [
            (Religiosity.VERY_RELIGIOUS, 0.05),      # 5% very religious
            (Religiosity.MODERATE_RELIGIOUS, 0.10),  # 10% moderate religious
            (Religiosity.OCCASIONAL_RELIGIOUS, 0.30), # 30% occasional religious
            (Religiosity.NO_RELIGION, 0.55),         # 55% no religion
        ]
    
    def _get_random_child_count(self) -> int:
        """Determine number of children based on distribution probabilities."""
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for child_count, probability in self.child_distribution:
            cumulative_prob += probability
            if rand_val <= cumulative_prob:
                return child_count
        
        # Fallback (should not reach here with valid probabilities)
        return 0
    
    def _get_random_religiosity(self) -> Religiosity:
        """Determine religiosity level based on distribution probabilities."""
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for religiosity, probability in self.religiosity_distribution:
            cumulative_prob += probability
            if rand_val <= cumulative_prob:
                return religiosity
        
        # Fallback (should not reach here with valid probabilities)
        return Religiosity.NO_RELIGION
    
    def _get_social_category_for_age(self, age: int) -> SocialCategory:
        """
        Determine social category based on age and realistic French demographic distribution.
        
        Uses INSEE data for population 15+ years:
        - Farmers: ~1.5%
        - Artisans/Merchants/Entrepreneurs: ~3.5%
        - Executives/Higher Intellectual: ~10.5%
        - Intermediate Professions: ~14.5%
        - Employees: ~15.5%
        - Workers: ~11.5%
        - Retirees: ~26.5%
        - Other Inactive: ~16.5%
        
        Args:
            age: Age of the person
            
        Returns:
            SocialCategory enum value
        """
        # Children under 15: inactive
        if age < 15:
            return SocialCategory.INACTIVE
        
        # Young people (15-17): mostly inactive (students) with some early workers
        elif age < 18:
            return random.choices(
                [SocialCategory.INACTIVE, SocialCategory.EMPLOYEES, SocialCategory.WORKERS],
                weights=[0.85, 0.10, 0.05]  # 85% inactive, 10% employees, 5% workers
            )[0]
        
        # Young adults (18-24): mix of inactive (students) and entry-level positions
        elif age < 25:
            return random.choices(
                [SocialCategory.INACTIVE, SocialCategory.EMPLOYEES, SocialCategory.WORKERS],
                weights=[0.50, 0.35, 0.15]  # 50% inactive, 35% employees, 15% workers
            )[0]
        
        # Adults (25-61): active professional categories based on INSEE data
        elif age < 62:
            return random.choices([
                SocialCategory.FARMERS,
                SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS,
                SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS,
                SocialCategory.INTERMEDIATE_PROFESSIONS,
                SocialCategory.EMPLOYEES,
                SocialCategory.WORKERS,
                SocialCategory.INACTIVE
            ], weights=[
                1.5,   # 1.5% farmers
                3.5,   # 3.5% artisans/merchants/entrepreneurs
                10.5,  # 10.5% executives/higher intellectual
                14.5,  # 14.5% intermediate professions
                15.5,  # 15.5% employees
                11.5,  # 11.5% workers
                43.5   # 43.5% inactive (includes unemployed, students, homemakers, etc.)
            ])[0]
        
        # Pre-retirement and seniors (62+): mostly retirees with some still active
        else:
            return random.choices([
                SocialCategory.RETIREES,
                SocialCategory.INACTIVE,
                SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS,
                SocialCategory.INTERMEDIATE_PROFESSIONS,
                SocialCategory.EMPLOYEES
            ], weights=[
                0.75,  # 75% retirees
                0.15,  # 15% inactive
                0.04,  # 4% still working executives
                0.03,  # 3% still working intermediate
                0.03   # 3% still working employees
            ])[0]
    
    def _generate_person(self, min_age: int = 0, max_age: int = 100) -> Person:
        """Generate a random person with random gender, age, and appropriate social category."""
        gender = random.choice(list(Gender))
        age = random.randint(min_age, max_age)
        social_category = self._get_social_category_for_age(age)
        return Person(gender=gender, age=age, social_category=social_category)
    
    def _generate_parents(self) -> List[Person]:
        """Generate parents for a family (typically 2 adults)."""
        # Generate 2 parents (adults aged 25-75)
        parent1 = self._generate_person(min_age=25, max_age=75)
        parent2 = self._generate_person(min_age=25, max_age=75)
        return [parent1, parent2]
    
    def _generate_children(self, count: int) -> List[Person]:
        """Generate children for a family."""
        children = []
        for _ in range(count):
            # Children aged 0-17
            child = self._generate_person(min_age=0, max_age=17)
            children.append(child)
        return children
    
    def generate_family(self) -> Family:
        """Generate a single family with random parents and children based on distribution."""
        # Determine family religiosity
        religiosity = self._get_random_religiosity()
        
        family = Family(religiosity=religiosity)
        
        # Add parents
        parents = self._generate_parents()
        for parent in parents:
            family.add_parent(parent)
        
        # Add children based on distribution
        child_count = self._get_random_child_count()
        if child_count > 0:
            children = self._generate_children(child_count)
            family.add_children(children)
        
        return family
    
    def generate_families(self, count: int) -> List[Family]:
        """Generate multiple families with the specified child distribution."""
        families = []
        for _ in range(count):
            family = self.generate_family()
            families.append(family)
        return families