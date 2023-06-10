import dataclasses


@dataclasses.dataclass
class TopCandidate:
    distance: float
    id: int
    passengers_amount: int
    source_location: list[float]
    estimated_cost: float
