#!/usr/bin/env python3
import curses
import re
from os import listdir
from importlib import import_module
from scrabblesolver_common import Cell, CELL_CH

# For debug only, TODO comment out
import logging
logging.basicConfig(filename='dbg.log', level=logging.DEBUG)
logging.info("Started")


def main(stdscr):
    # curses.start_color()  # Already done by wrapper if terminal supports it
    curses.init_pair(Cell.BEGIN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(Cell.L2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(Cell.L3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(Cell.W2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(Cell.W3, curses.COLOR_RED, curses.COLOR_BLACK)

    curses.echo()

    # Available language configurations
    langs = [re.search(r'^scrabblesolver_([a-z]{2})\.py$', fn) for fn in listdir()]
    langs = [m.group(1) for m in langs if m is not None]
    stdscr.addstr(0, 0, " Languages available ", curses.A_REVERSE)
    for i in range(len(langs)):
        stdscr.addstr(i // 2 + 1, 10 * (i % 2) + 1,
                      "{}.{}".format(i + 1, langs[i].upper()))
    while True:
        try:
            stdscr.addstr((len(langs) - 1) // 2 + 2, 0, "Choose language:   ")
            ch = int(stdscr.getstr((len(langs) - 1) // 2 + 2, 17, 2)) -1
            if 0 <= ch < len(langs):
                break
        except Exception:
            pass
    lang = import_module("scrabblesolver_{}".format(langs[ch]))
    stdscr.clear()
    stdscr.refresh()

    # Create window for the game table
    W, H = len(lang.TABLE[0]), len(lang.TABLE)
    wtable = curses.newwin(H + 2, W + 2, 0, 0)
    wtable.border()
    wtable.addstr(0, 1 + (W - 10) // 2, "Game table", curses.A_REVERSE)
    for i in range(H):
        for j in range(W):
            cell = lang.TABLE[i][j]
            wtable.addch(i + 1, j + 1, CELL_CH[cell], curses.color_pair(cell))

    curses.curs_set(2)
    # Convert esc sequences (like those for arrows) into curses-standard codes
    wtable.keypad(True)
    wtable.refresh()

    # Create window for help/explanation
    WH = 29
    whelp = curses.newwin(13, WH + 2, 4, W + 4)
    whelp.border()
    whelp.addstr(0, 1 + (WH - 15) // 2, "Help & Commands", curses.A_REVERSE)
    whelp.addstr(1, 1, "[  1  ] Type your letters")
    whelp.addstr(2, 1, "[  2  ] Find best word")
    whelp.addstr(3, 1, "[  0  ] Exit")
    whelp.addstr(4, 1, "[SPACE] Switch horiz./vert.")
    whelp.addstr(5, 1, "[←↑ ↓→] Move in table")
    whelp.addstr(6, 1, "[ DEL ] Delete letter")
    whelp.addstr(7, 1, "[PAG↑↓] Prev./next found word")
    whelp.addstr(8, 1, "[ENTER] Accept chosen word")
    whelp.addstr(9, 1, "[  *  ] Jolly card")
    def status(s):
        if len(s) <= WH:
            s = "{0:^{1}}".format(s, WH)
        else:
            s = s[:WH]
        whelp.addstr(11, 1, s)
        whelp.refresh()
    status("Table input, horizontal")

    # Create a window for color legend
    WL = 16
    wlegnd = curses.newwin(11, WL + 2, 0, W + WH + 8)
    wlegnd.border()
    wlegnd.addstr(0, 1 + (WL - 13) // 2, "Colors legend", curses.A_REVERSE)
    wlegnd.addstr(1, 1, "* Normal cells", curses.color_pair(Cell.SIMPLE))
    wlegnd.addstr(2, 1, "* Beginning cell", curses.color_pair(Cell.BEGIN))
    wlegnd.addstr(3, 1, "* Letter x2", curses.color_pair(Cell.L2))
    wlegnd.addstr(4, 1, "* Letter x3", curses.color_pair(Cell.L3))
    wlegnd.addstr(5, 1, "* Word x2", curses.color_pair(Cell.W2))
    wlegnd.addstr(6, 1, "* Word x3", curses.color_pair(Cell.W3))
    wlegnd.addstr(8, 1, "Sometimes colors")
    wlegnd.addstr(9, 1, " don't work :(  ")
    wlegnd.refresh()

    # Create window for holding your letter cards
    WC = max(12, lang.NCARDS)
    wcards = curses.newwin(3, WC + 2, 0, W + 4 + (WH - WC) // 2)
    wcards.border()
    wcards.addstr(0, 1 + (WC - 12) // 2, "Your letters", curses.A_REVERSE)
    wcards.refresh()

    # Current position, letters on table, letters on ledger, direction
    X, Y = 0, 0
    TABLE = [" " * W] * H  # TABLE stores letters only
    TABJ = [[False] * W] * H  # TABJ stores which letters are placed as a jolly
    CARDS = ""
    VERT = False  # Vertical input
    # Main loop
    curses.noecho()
    while True:
        k = wtable.getkey(Y + 1, X + 1).upper()
        if k == "1":
            status("[ENTER] to stop typing")
            wcards.addstr(1, 1 + (WC - lang.NCARDS) // 2, " " * lang.NCARDS)
            curses.echo()
            CARDS = str(wcards.getstr(1, 1 + (WC - lang.NCARDS) // 2, lang.NCARDS), encoding='utf8').upper()
            curses.noecho()
            CARDS = "".join(x for x in CARDS if x in lang.LETTERS)
            wcards.addstr(1, 1 + (WC - lang.NCARDS) // 2, " " * lang.NCARDS)
            wcards.addstr(1, 1 + (WC - lang.NCARDS) // 2, CARDS)
            wcards.refresh()
            status("Table input, " + ("vertical" if VERT else "horizontal"))
        elif k == "2":
            pass  # TODO
        elif k == "0":
            break  # Exit
        elif k == " ":
            VERT = not VERT
            status("Table input, " + ("vertical" if VERT else "horizontal"))
        elif k == "KEY_UP":
            Y = max(0, Y - 1)
        elif k == "KEY_DOWN":
            Y = min(H - 1, Y + 1)
        elif k == "KEY_LEFT":
            X = max(0, X - 1)
        elif k == "KEY_RIGHT":
            X = min(W - 1, X + 1)


curses.wrapper(main)
