import itertools

from .resistor import Resistor
from .voltage_source import VoltageSource
from .ground import Ground

COMPONENT_CATEGORY_MAPS = {
    "Resistors": sorted([Resistor], key=lambda cls: cls.__name__),
    "Sources": sorted([VoltageSource, Ground], key=lambda cls: cls.__name__),
}

all = []
for components in COMPONENT_CATEGORY_MAPS.values():
    all.extend(components)

COMPONENT_CATEGORY_MAPS["All"] = sorted(all, key=lambda cls: cls.__name__)
