import dataclasses
from typing import Optional

@dataclasses.dataclass
class OrderStatusResponse:
    orderId: str
    orderStatus: str
    orderType: str
    amount: float
    creationDate: str
    wikifolioSymbol: Optional[str] = None
    executionPrice: Optional[float] = None
    statusDate: Optional[str] = None
    reason: Optional[int] = None
    stop: Optional[float] = None
    limit: Optional[float] = None
    