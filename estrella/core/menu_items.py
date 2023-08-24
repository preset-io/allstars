from typing import List, Optional
from estrella.core.base import Serializable

class MenuItem(Serializable):
    """Any object living in the SemanticLayer's menu"""

    def __init__(self, key: str, label: Optional[str] = None, description: Optional[str] = None):
        self.key = key
        self.label = label
        self.description = description


class _SqlExpression(MenuItem):
    """Private class for something that lives in a SELECT"""

    def __init__(self, expression: str, relation_key: str = None, relation_keys: List[str] = None, *args, **kwargs):
        if relation_key is None and (relation_keys is None or not relation_keys):
            raise ValueError("Either relation_key or relation_keys must be provided.")

        if relation_key:
            relation_keys = [relation_key]

        self.expression = expression
        self.relation_keys = relation_keys if relation_keys is not None else []

        super().__init__(*args, **kwargs)


class Metric(_SqlExpression):
    """Just a good old metric"""

    pass


class Dimension(_SqlExpression):
    """A simple dimension"""

    pass


class Filter(_SqlExpression):
    """
    A predefined filter that can be added to a WHERE clause
    """

    pass


class Folder(MenuItem):
    def __init__(self, key: str, parent_folder_key: Optional[str] = None, label: Optional[str] = None, description: Optional[str] = None):
        super().__init__(key, label, description)
        self.parent_folder_key = parent_folder_key

