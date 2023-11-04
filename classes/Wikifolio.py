import dataclasses
from typing import Optional, List

from classes.Position import Position

@dataclasses.dataclass
class Wikifolio:
    wikifolioStatus = str
    cashAccountCurrentBalance: float
    totalValue: float
    wikifolioSymbol: Optional[str] = None
    bidPrice: Optional[float] = None
    askPrice: Optional[float] = None
    priceDate: Optional[str] = None
    baseCurrency: Optional[str] = None
    positions: List[Position] = dataclasses.field(default_factory=list)