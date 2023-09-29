from typing import List, Optional
from estrella.core.base import MenuItem


class Folder(MenuItem):
    def __init__(
        self,
        key: str,
        parent_folder_key: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        folders=None,
    ):
        super().__init__(key, label, description)
        self.parent_folder_key = parent_folder_key
        self._folders = folders or []

    def flatten(self, l):
        l.append(self)
        for f in self._folders:
            f["parent_folder_key"] = self.key
            f = Folder.from_dict(f)
            f.flatten(l)

    def to_dict(self):
        return {
            "key": self.key,
            "label": self.label,
            "parent_folder_key": self.parent_folder_key,
            "description": self.description,
        }
