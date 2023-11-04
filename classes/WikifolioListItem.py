import dataclasses
from typing import Optional

@dataclasses.dataclass
class WikifolioListItem:
    wikifolioSymbol: Optional[str] = None
    resourceLink: Optional[str] = None