import os
from typing import List, Optional
import yaml

from dataclasses import asdict, is_dataclass, fields


class Serializable:
    """Serializable mixin providing serialization to/from dictionary and YAML."""

    def to_dict(self) -> dict:
        """Converts the object to a dictionary, including properties."""
        if is_dataclass(self.__class__):
            d = {}
            for field in fields(self):
                value = getattr(self, field.name)
                if hasattr(value, "to_serializable"):
                    d[field.name] = value.to_serializable()
                else:
                    d[field.name] = value

            props = {name: getattr(self, name) for name in self.properties()}
            return {**props, **d}
        else:
            raise Exception("Nah gotta provide a to_serializable for non-dataclass")

    def to_serializable(self) -> dict:
        return self.to_dict()

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

    def to_yaml(self, key=None) -> str:
        """Converts the object to a YAML string."""
        obj = self.to_serializable()
        if key and key in obj:
            obj = obj[key]
        return yaml.dump(obj, sort_keys=False)

    def to_yaml_file(self, filename: str, wrap_under: str = None) -> None:
        """Writes the object to a YAML file."""
        d = self.to_serializable()
        if wrap_under:
            d = {wrap_under: d}
        with open(filename, "w") as file:
            yaml.dump(d, file, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_string: str):
        """Creates an instance of the class from a YAML string, excluding properties."""
        data = None
        try:
            data = yaml.load(yaml_string, Loader=yaml.FullLoader)
        except:
            pass
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, filename: str, verbose: bool = True):
        """Creates an instance of the class from a YAML file, excluding properties."""
        with open(filename, "r") as file:
            print(f"Loading file {filename}")
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

    def to_dict(self):
        return {
            "key": self.key,
            "label": self.label,
            "description": self.description,
        }


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

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {
                "expression": self.expression,
                "relation_keys": self.relation_keys,
            }
        )
        return d


class SerializableCollection(dict, Serializable):
    def __init__(self, l: list = None):
        l = l or []
        for o in l:
            self[o.key] = o

    def to_serializable(self):
        l = []
        for o in self:
            if hasattr(o, "to_dict"):
                o = o.to_dict()
            l.append(o)
        return l

    @classmethod
    def from_yaml_file(cls, filename: str, object_class: Serializable, key: str = None):
        """Creates an instance of the class from a YAML file, excluding properties."""
        data = None
        try:
            with open(filename, "r") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
        except:
            pass
        if key and data:
            data = data.get(key)
        if data:
            data = [object_class.from_dict(o) for o in data]
        return cls(data)

    def append(self, obj):
        self[obj.key] = obj

    def upsert(self, collection):
        self.update(collection)

    def __iter__(self):
        return iter(self.values())
