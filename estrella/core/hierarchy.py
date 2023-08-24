from dataclasses import dataclass, field
from typing import List
from estrella.core.menu_items import Dimension


@dataclass
class Hierarchy:
    key: str
    dimensions: List[Dimension] = field(default_factory=list)
