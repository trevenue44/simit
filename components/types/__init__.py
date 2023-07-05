from enum import Enum
from typing import Dict, List


class ComponentCategory(Enum):
    RESISTOR = "RESISTOR"
    SOURCE = "SOURCE"


componentDataType = Dict[str, List[str]]
simulationResultsType = Dict[str, List[str]]
