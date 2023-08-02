from . import GeneralComponent


class ComponentAndTerminalIndex:
    def __init__(self, component: GeneralComponent, terminalIndex: int) -> None:
        self.component = component
        self.terminalIndex = terminalIndex
