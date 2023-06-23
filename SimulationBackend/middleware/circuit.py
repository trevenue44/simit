from typing import List, Dict

from .circuit_node import CircuitNode


class Circuit:
    name = "Circuit"

    def __init__(self, circuitCount: int) -> None:
        self.uniqueID = f"{self.name}-{circuitCount}"
        self.nodes: List[CircuitNode] = []
        self.components = {}
