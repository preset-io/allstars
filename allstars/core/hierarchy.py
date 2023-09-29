from dataclasses import dataclass, field
from typing import List
from allstars.core.dimension import Dimension


@dataclass
class Hierarchy:
    key: str
    dimensions: List[Dimension] = field(default_factory=list)
