from dataclasses import dataclass


@dataclass
class Contract:
    user: str
    yearly_price: int
    length: int
    entries: int
