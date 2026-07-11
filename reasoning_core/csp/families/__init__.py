"""Thin family adapters over the common CSP semantic core."""

from .assignment import AssignmentFamily
from .graph import GraphFamily
from .grid import GridFamily
from .numeric import NumericFamily
from .scheduling import SchedulingFamily
from .sets import SetFamily

FAMILIES = {
    "assignment": AssignmentFamily(), "graph": GraphFamily(), "grid": GridFamily(),
    "numeric": NumericFamily(), "scheduling": SchedulingFamily(), "sets": SetFamily(),
}

ALIASES = {"attribute": "assignment", "linear": "numeric", "set": "sets"}


def get_family(name):
    return FAMILIES[ALIASES.get(name, name)]

