# Common parts of different Scrabble solver languages
from enum import IntEnum

__ALL__ = ['Cell', 'CELL_CH']


class Cell(IntEnum):
    """Integral values are also wired to curses color pair numbers."""
    SIMPLE = 0  # Nothing special
    BEGIN = 1  # Beginning cell
    L2 = 2  # Double letter
    L3 = 3  # Triple letter
    W2 = 4  # Double word
    W3 = 5  # Triple word


CELL_CH = {Cell.SIMPLE: ' ', Cell.BEGIN: '2', Cell.L2: '2', Cell.L3: '3',
           Cell.W2: '2', Cell.W3: '3'}
