from .resistor import Resistor
from .voltage_source import VoltageSource
from .ground import Ground

COMPONENT_CATEGORY_MAPS = {"Resistors": [Resistor], "Sources": [VoltageSource, Ground]}
