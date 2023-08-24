@dataclass
class MenuItem:
    """Any object living in the SemanticLayer's menu"""

    key: str
    label: Optional[str] = None
    description: Optional[str] = None


@dataclass
class _SqlExpression(MenuItem):
    """Private class for something that lives in a SELECT"""

    expression: str

    # Usually a single relation is involved, but sometimes two
    # as in SUM(DATE_DIFF(A.dt, B.dt))
    relation_keys: List[str]


@dataclass
class Metric(_SqlExpression):
    """Just a good old metric"""

    pass


@dataclass
class Dimension(_SqlExpression):
    """A simple dimension"""

    pass


@dataclass
class Filter(_SqlExpression):
    """
    A predefined filter that can be added to a WHERE clause
    """

    pass


@dataclass
class Folder(MenuItem):
    parent_folder_key: Optional[str] = None
