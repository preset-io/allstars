import os
import yaml

from dataclasses import asdict


class Serializable:
    """Serializable mixin providing serialization to/from dictionary and YAML."""

    def to_dict(self) -> dict:
        """Converts the object to a dictionary, including properties."""
        d = asdict(self)
        props = {name: getattr(self, name) for name in self.properties()}
        return {**props, **d}

    @classmethod
    def properties(cls) -> set:
        """Finds all properties in the class."""
        return {
            name for name, value in vars(cls).items() if isinstance(value, property)
        }

    @classmethod
    def from_dict(cls, d: dict):
        """Creates an instance of the class from a dictionary, excluding properties."""
        filtered_dict = {
            key: value for key, value in d.items() if key not in cls.properties()
        }
        return cls(**filtered_dict)

    def to_yaml(self) -> str:
        """Converts the object to a YAML string."""
        return yaml.dump(self.to_dict(), sort_keys=False)

    def to_yaml_file(self, filename: str) -> None:
        """Writes the object to a YAML file."""
        with open(filename, "w") as file:
            yaml.dump(self.to_dict(), file, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_string: str):
        """Creates an instance of the class from a YAML string, excluding properties."""
        data = yaml.load(yaml_string, Loader=yaml.FullLoader)
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, filename: str):
        """Creates an instance of the class from a YAML file, excluding properties."""
        with open(filename, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return cls.from_dict(data)


class MenuItem(Serializable):
    """Any object living in the SemanticLayer's menu"""

    def __init__(
        self, key: str, label: Optional[str] = None, description: Optional[str] = None
    ):
        self.key = key
        self.label = label
        self.description = description


class _SqlExpression(MenuItem):
    """Private class for something that lives in a SELECT"""

    def __init__(
        self,
        expression: str,
        relation_key: str = None,
        relation_keys: List[str] = None,
        *args,
        **kwargs,
    ):
        if relation_key is None and (relation_keys is None or not relation_keys):
            raise ValueError("Either relation_key or relation_keys must be provided.")

        if relation_key:
            relation_keys = [relation_key]

        self.expression = expression
        self.relation_keys = relation_keys if relation_keys is not None else []

        super().__init__(*args, **kwargs)
