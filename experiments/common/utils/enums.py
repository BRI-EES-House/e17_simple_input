from enum import Enum, unique


@unique
class Direction(str, Enum):
    N  = 'n'
    NE = 'ne'
    E  = 'e'
    SE = 'se'
    S  = 's'
    SW = 'sw'
    W  = 'w'
    NW = 'nw'
    TOP = 'top'
    BOTTOM = 'bottom'
