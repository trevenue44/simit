from .resistor import Resistor
from .voltage_source import VoltageSource
from .ground import Ground
from .wire import Wire

COMPONENT_CLASSES = sorted(
    [Resistor, VoltageSource, Ground], key=lambda cls: cls.__name__
)


from .types import ComponentCategory


def getComponentClasses(
    category: ComponentCategory | None = None, searchText: str | None = None
):
    result = COMPONENT_CLASSES
    if category:
        result = list(filter(lambda compCls: compCls.category == category, result))
    if searchText:
        result = list(
            filter(
                lambda compCls: (searchText.lower() in compCls.name.lower())
                or (searchText.lower() in compCls.category.value.lower()),
                result,
            )
        )
    return result
