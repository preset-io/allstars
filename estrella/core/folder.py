from typing import List, Optional
from estrella.core.base import MenuItem


class Folder(MenuItem):
    def __init__(
        self,
        key: str,
        parent_folder_key: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(key, label, description)
        self.parent_folder_key = parent_folder_key
