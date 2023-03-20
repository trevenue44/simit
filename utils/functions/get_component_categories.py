from components import COMPONENT_CATEGORY_MAPS


def get_component_categories() -> list[str]:
    """
    Returns a list of all the component categories available.
    """
    return COMPONENT_CATEGORY_MAPS.keys()
