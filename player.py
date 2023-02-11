from dataclasses import dataclass
import contract


@dataclass
class Player:
    """ Class for Legend Bowl players"""
    first_name: str
    last_name: str
    pos: str
    college: str
    rating: int
    potential: int
    trait: str
    age: int
    former_team: str
    timeframe: str
    contract: contract.Contract


