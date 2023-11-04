import dataclasses
from typing import Optional

@dataclasses.dataclass
class Underlying:
    isin: Optional[str] = None