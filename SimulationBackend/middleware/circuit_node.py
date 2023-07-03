from typing import List, Tuple, Dict


class CircuitNode:
    name = "CircuitNode"

    def __init__(self, nodeCount: int) -> None:
        self.uniqueID = f"{self.name}-{nodeCount}"
        self.componentTerminals: List[Tuple[str, int]] = []
        self.data: Dict[str, List[str]] = {}
