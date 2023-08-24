from dataclasses import dataclass
from functools import partial

kw_only_dataclass = partial(dataclass, kw_only=True)
