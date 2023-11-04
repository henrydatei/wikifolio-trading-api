import dataclasses
from typing import Optional

@dataclasses.dataclass
class Position:
    quantity: float
    underlying: Optional[str] = None
    averagePurchasePrice: Optional[float] = None