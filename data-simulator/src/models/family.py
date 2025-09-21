"""Family class for representing family data."""

import uuid
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from person import Person, Religiosity


class Family:
    """Represents a family with a unique identifier, family members, and religiosity level."""
    
    def __init__(self, religiosity: Optional["Religiosity"] = None, family_id: Optional[str] = None):
        """
        Initialize a Family instance.
        
        Args:
            religiosity: Religiosity level of the family (Religiosity enum)
            family_id: Optional family identifier. If not provided, a UUID will be generated.
        """
        self.family_id = family_id or str(uuid.uuid4())
        self.parents: List["Person"] = []
        self.children: List["Person"] = []
        self.religiosity = religiosity
    
    def add_parent(self, parent: "Person") -> None:
        """Add a parent to the family."""
        if parent not in self.parents:
            self.parents.append(parent)
    
    def add_child(self, child: "Person") -> None:
        """Add a child to the family."""
        if child not in self.children:
            self.children.append(child)
    
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
        religiosity_str = f", {self.religiosity.value}" if self.religiosity else ", no_religiosity_set"
        return f"Family(id={self.family_id[:8]}..., {len(self.parents)} parents, {len(self.children)} children{religiosity_str})"
    
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