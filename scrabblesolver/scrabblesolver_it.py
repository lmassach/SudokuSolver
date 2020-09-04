# Configuration file for solving Scrabble in italian.
from scrabblesolver_common import Cell
import re
from os.path import join, isfile, dirname, abspath

__ALL__ = ['DICT', 'LETTERS', 'POINTS', 'TABLE']


# Dictionary file
DICTFN = ["/usr/share/dict/italian",
          join(dirname(abspath(__file__)), "italian.dict")]
# Dictionary word filter: only words with the (21) italian letters plus the
# accented ones; only lowercase characters to cut out names; only 2+ letters
# words that fit in the table (<= 17 letters).
RE_DICT_FILTER = re.compile(r'^[abcdefghilmnopqrstuvzàèéìòù]{2,17}$')
# Dictionary letter substitution (aka accent removal)
DICT_SUBS = {'à': 'a', 'è' : 'e', 'é': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}
# Dictionary loading
DICT = set()
for fp in DICTFN:
    if isfile(fp):
        with open(fp) as ifs:
            for word in ifs:
                word = word.strip()  # Cut blanks and newlines
                if RE_DICT_FILTER.search(word) is not None:
                    for k, v in DICT_SUBS.items():
                        word = word.replace(k, v)
                    DICT.add(word.upper())
if len(DICT) == 0:
    raise RuntimeError("No dictionary file was found.")
# Special words allowed (acronyms, etc.)
DICT |= {  # Set in-place union
    # TODO aggiungere targhe, sigle degli stati, etc.
    'AN'
}

# How many of each letter
LETTERS = {
    'A': 12, 'E': 12, 'I': 12, 'O': 12, 'U': 4,
    'C': 7, 'R': 7, 'S': 7, 'T': 7,
    'L': 6, 'M': 6, 'N': 6,
    'B': 4, 'D': 4, 'F': 4, 'G': 4, 'P': 4, 'V': 4,
    'H': 2, 'Q': 2, 'Z': 2,
    '*': 2
}
# How many points per letter
POINTS = {
    '*': 0,
    'A': 1, 'C': 1, 'E': 1, 'I': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1,
    'L': 2, 'M': 2, 'N': 2,
    'P': 3,
    'B': 4, 'D': 4, 'F': 4, 'G': 4, 'U': 4, 'V': 4,
    'H': 8, 'Z': 8,
    'Q': 10
}
# Table cell types
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

# Letter cards held by the player
NCARDS = 8
# Extra points for using many letter cards
EXTRA_N = {6: 20, 7: 40, 8: 60}  # w/o jolly
EXTRA_NJ = {6: 10, 7: 30, 8: 50}  # w/ jolly
# Extra points for special words
EXTRA_W = {'SCARABEO': 100, 'SCARABEI': 100}
