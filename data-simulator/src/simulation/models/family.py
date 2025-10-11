"""Family class for representing family data."""

import uuid
from typing import List, Optional, TYPE_CHECKING
from .person import SocialCategory

if TYPE_CHECKING:
    from .person import Person, Religiosity
    from .location import Position


class Family:
    """Represents a family with a unique identifier, family members, religiosity level, and home location."""

    def __init__(
        self,
        religiosity: Optional["Religiosity"] = None,
        social_category: Optional["SocialCategory"] = None,
        family_id: Optional[str] = None,
        home_position: Optional["Position"] = None,
    ):
        """
        Initialize a Family instance.

        Args:
            religiosity: Religiosity level of the family (Religiosity enum)
            social_category: Social/professional category of the family (SocialCategory enum)
            family_id: Optional family identifier. If not provided, a UUID will be generated.
            home_position: Geographic position of the family home (Position object)
        """
        self.family_id = family_id or str(uuid.uuid4())
        self.parents: List["Person"] = []
        self.children: List["Person"] = []
        self.religiosity = religiosity
        self.social_category = social_category
        self.home_position = home_position

    def add_parent(self, parent: "Person") -> None:
        """Add a parent to the family and set the family reference on the person."""
        if parent not in self.parents:
            self.parents.append(parent)
            parent.family = self

    def add_child(self, child: "Person") -> None:
        """Add a child to the family and set the family reference on the person."""
        if child not in self.children:
            self.children.append(child)
            child.family = self

    def add_children(self, children: List["Person"]) -> None:
        """Add multiple children to the family."""
        for child in children:
            self.add_child(child)

    @property
    def total_members(self) -> int:
        """Return total number of family members."""
        return len(self.parents) + len(self.children)

    @property
    def num_children(self) -> int:
        """Return number of children in the family."""
        return len(self.children)

    def __str__(self) -> str:
        """Return string representation of the family."""
        religiosity_str = (
            f", {self.religiosity.value}"
            if self.religiosity
            else ", no_religiosity_set"
        )
        social_category_str = (
            f", {self.social_category.value}"
            if self.social_category
            else ", no_social_category_set"
        )
        return f"Family(id={self.family_id[:8]}..., {len(self.parents)} parents, {len(self.children)} children{religiosity_str}{social_category_str})"

    def __repr__(self) -> str:
        """Return detailed string representation of the family."""
        return f"Family(family_id='{self.family_id}', parents={len(self.parents)}, children={len(self.children)}, religiosity={self.religiosity})"

    def __eq__(self, other) -> bool:
        """Check equality based on family_id."""
        if not isinstance(other, Family):
            return False
        return self.family_id == other.family_id

    def __hash__(self) -> int:
        """Return hash based on family_id."""
        return hash(self.family_id)
