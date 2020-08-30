#!/usr/bin/env python3
from enum import Enum

# Dictionary file
DICT = "/usr/share/dict/italian"
# How many of each letter
LETTERS = {
    'A': 12, 'E': 12, 'I': 12, 'O': 12, 'U': 4,
    'C': 7, 'R': 7, 'S': 7, 'T': 7,
    'L': 6, 'M': 6, 'N': 6,
    'B': 4, 'D': 4, 'F': 4, 'G': 4, 'P': 4, 'V': 4,
    'H': 2, 'Q': 2, 'Z': 2
}
# How many points per letter
POINTS = {
    'A': 1, 'C': 1, 'E': 1, 'I': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1,
    'L': 2, 'M': 2, 'N': 2,
    'P': 3,
    'B': 4, 'D': 4, 'F': 4, 'G': 4, 'U': 4, 'V': 4,
    'H': 8, 'Z': 8,
    'Q': 10
}
# Table cell types
class Cell(Enum):
    SIMPLE = 0
    BEGIN = 1  # Beginning cell
    L2 = 12  # Double letter
    L3 = 13  # Triple letter
    W2 = 22  # Double word
    W3 = 23  # Triple word
TABLE = (
    "W   l   W   l   W\n" +
    " w    L   L    w \n" +
    "  w    l l    w  \n" +
    "   w    l    w   \n" +
    "l   w       w   l\n" +
    "     w     w     \n" +
    " L    L   L    L \n" +
    "  l    l l    l  \n" +
    "W  l    B    l  W\n" +
    "  l    l l    l  \n" +
    " L    L   L    L \n" +
    "     w     w     \n" +
    "l   w       w   l\n" +
    "   w    l    w   \n" +
    "  w    l l    w  \n" +
    " w    L   L    w \n" +
    "W   l   W   l   W\n"
)
_ = {' ': Cell.SIMPLE, 'B': Cell.BEGIN, 'l': Cell.L2, 'L': Cell.L3,
     'w': Cell.W2, 'W': Cell.W3}
TABLE = [[_[y] for y in x] for x in TABLE.splitlines()]
