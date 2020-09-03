#!/usr/bin/env python3
import curses
import re
from os import listdir
from importlib import import_module
from scrabblesolver_common import Cell, CELL_CH

# For debug only
import logging
logging.basicConfig(filename='dbg.log', level=logging.DEBUG)
# logging.disable()  # TODO uncomment when debug is not needed
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
    # TODO incroci con altre parole? Li gestisce l'utente!
    def get_points(word, starty, startx, vert, table, tabj, cards):
        """
        Get value (points) of a word `w` starting at the given position
        `start*`, going vertical if `vert` is True, on a table already populated
        as in `table` with jollys on `tabj`, given that you have `cards` on the
        ledger. Return 0 if you can't put that word in that position.
        The word must fit within the table.
        """
        points = 0
        wmul = 1
        cards = list(cards)
        icards = len(cards)
        jollys = []
        for k in range(len(word)):
            jolly = False
            i = starty + (k if vert else 0)
            j = startx + (0 if vert else k)
            if table[i][j] == " ":
                if word[k] in cards:
                    cards.remove(word[k])
                    lmul = 2 if lang.TABLE[i][j] == Cell.L2 else (
                        3 if lang.TABLE[i][j] == Cell.L3 else 1
                    )
                    points += lang.POINTS[word[k]] * lmul
                elif "*" in cards:
                    cards.remove("*")
                    jolly = True
                else:
                    return 0, None
                wmul *= 2 if lang.TABLE[i][j] == Cell.W2 else (
                    3 if lang.TABLE[i][j] == Cell.W3 else 1
                )
            else:
                if word[k] != table[i][j]:
                    return 0, None
                if not tabj[i][j]:
                    lmul = 2 if lang.TABLE[i][j] == Cell.L2 else (
                        3 if lang.TABLE[i][j] == Cell.L3 else 1
                    )
                    points += lang.POINTS[word[k]] * lmul
                else:
                    jolly = True
                wmul *= 2 if lang.TABLE[i][j] == Cell.W2 else (
                    3 if lang.TABLE[i][j] == Cell.W3 else 1
                )
            jollys.append(jolly)
        extra = 0
        dcards = icards - len(cards)
        if any(jollys):
            if dcards in lang.EXTRA_NJ:
                extra += lang.EXTRA_NJ[dcards]
        else:
            if dcards in lang.EXTRA_N:
                extra += lang.EXTRA_N[dcards]
        if word in lang.EXTRA_W:
            extra += lang.EXTRA_W[word]
        return wmul * points + extra, jollys
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
            wtable.addstr(i + 1, j + 1, CELL_CH[cell], curses.color_pair(cell))

    curses.curs_set(2)
    # Convert esc sequences (like those for arrows) into curses-standard codes
    wtable.keypad(True)
    wtable.refresh()

    # Create window for help/explanation
    WH = 31
    whelp = curses.newwin(12, WH + 2, 4, W + 4)
    def status(s):
        """Replaces the status message (help window's last line)."""
        if len(s) <= WH:
            s = "{0:^{1}}".format(s, WH)
        else:
            s = s[:WH]
        whelp.addstr(10, 1, s)
        whelp.refresh()
    def finderkeys(b):
        """
        Changes the help displayed between word-finding mode (when b is True)
        and normal (table-input) mode (when b is False).
        """
        whelp.clear()
        whelp.border()
        whelp.addstr(0, 1 + (WH - 15) // 2, "Help & Commands", curses.A_REVERSE)
        if b:
            whelp.addstr(1, 1, "[PAG↑↓] Prev./next found word")
            whelp.addstr(2, 1, "[←↑ ↓→] Prev./next found word")
            whelp.addstr(3, 1, "[ENTER] Accept chosen word")
            whelp.addstr(4, 1, "[  0  ] Back to input mode")
        else:
            whelp.addstr(1, 1, "[  1  ] Type your letters")
            whelp.addstr(2, 1, "[  2  ] Find best word")
            whelp.addstr(3, 1, "[  0  ] Exit")
            whelp.addstr(4, 1, "[SPACE] Switch horiz./vert.")
            whelp.addstr(5, 1, "[←↑ ↓→] Move in table")
            whelp.addstr(6, 1, "[ DEL ] Delete letter")
            whelp.addstr(7, 1, "[  *  ] Jolly card")
            whelp.addstr(8, 1, "[ TAB ] Show jolly/letter")
        whelp.refresh()
    finderkeys(False)
    status("Table input, horizontal")

    # Create a window for color legend
    WL = 16
    wlegnd = curses.newwin(8, WL + 2, 0, W + WH + 8)
    wlegnd.border()
    wlegnd.addstr(0, 1 + (WL - 13) // 2, "Colors legend", curses.A_REVERSE)
    wlegnd.addstr(1, 1, "* Normal cells", curses.color_pair(Cell.SIMPLE))
    wlegnd.addstr(2, 1, "* Beginning cell", curses.color_pair(Cell.BEGIN))
    wlegnd.addstr(3, 1, "* Letter x2", curses.color_pair(Cell.L2))
    wlegnd.addstr(4, 1, "* Letter x3", curses.color_pair(Cell.L3))
    wlegnd.addstr(5, 1, "* Word x2", curses.color_pair(Cell.W2))
    wlegnd.addstr(6, 1, "* Word x3", curses.color_pair(Cell.W3))
    # wlegnd.addstr(8, 1, "Sometimes colors")
    # wlegnd.addstr(9, 1, " don't work :(  ")
    wlegnd.refresh()

    # Create a window for info about the dictionary
    wdicti = curses.newwin(4, WL + 2, 12, W + WH + 8)
    wdicti.border()
    wdicti.addstr(0, 1 + (WL - 10) // 2, "Dictionary", curses.A_REVERSE)
    wdicti.addstr(1, 1, "{0:^{1},d}".format(len(lang.DICT), WL))
    wdicti.addstr(2, 1 + (WL - 11) // 2, "known words")
    wdicti.refresh()

    # Create window for holding your letter cards
    WC = max(12, lang.NCARDS)
    wcards = curses.newwin(3, WC + 2, 0, W + 4 + (WH - WC) // 2)
    wcards.border()
    wcards.addstr(0, 1 + (WC - 12) // 2, "Your letters", curses.A_REVERSE)
    wcards.refresh()

    # Current position, letters on table, letters on ledger, direction
    X, Y = 0, 0
    TABLE = [[" "] * W for _ in range(H)]  # TABLE stores letters only
    TABJ = [[False] * W for _ in range(H)]  # TABJ stores which letters are placed as a jolly
    CARDS = ""
    VERT, J = False, True  # Vertical input, show jollys (vs show their letter)
    # TODO variable for solution currently being shown
    # Main loop
    curses.noecho()
    while True:
        k = wtable.getkey(Y + 1, X + 1).upper()
        # logging.debug("Keycode = " + repr(k))
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
            # Word finding
            finderkeys(True)
            status("Looking for words...")
            if CARDS == "":
                status("No letters!")
                wtable.getkey(Y + 1, X + 1)
            else:
                fWORDS = {}  # Dict of tuples word: (jollys, starty, startx, vert, points)
                for i in range(H):
                    for j in range(W):
                        # Look for horizontal words matching the letters
                        # already on the board/table
                        lmin = [k for k in range(j, W) if TABLE[i][k] != " " or lang.TABLE[i][k] == Cell.BEGIN]
                        if j < W - 1 and len(lmin) != 0 and (j == 0 or TABLE[i][j - 1] == " "):
                            lmin = max(2, lmin[0] - j + 1)
                            for w in lang.DICT:
                                if lmin <= len(w) <= W - j and (j + len(w) == W or TABLE[i][j + len(w)] == " "):
                                    pts, js = get_points(w, i, j, False, TABLE, TABJ, CARDS)
                                    if pts != 0:
                                        if w not in fWORDS or fWORDS[w][-1] < pts:
                                            fWORDS[w] = (js, i, j, False, pts)
                        # Look for vertical words matching the letters
                        # already on the board/table
                        lmin = [k for k in range(i, H) if TABLE[k][j] != " " or lang.TABLE[k][j] == Cell.BEGIN]
                        if i < H - 1 and len(lmin) != 0 and (i == 0 or TABLE[i - 1][j] == " "):
                            lmin = max(2, lmin[0] - i + 1)
                            for w in lang.DICT:
                                if lmin <= len(w) <= H - i and (i + len(w) == H or TABLE[i + len(w)][j] == " "):
                                    pts, js = get_points(w, i, j, True, TABLE, TABJ, CARDS)
                                    if pts != 0:
                                        if w not in fWORDS or fWORDS[w][-1] < pts:
                                            fWORDS[w] = (js, i, j, True, pts)
                if len(fWORDS) == 0:
                    status("No word found.")
                    wtable.getkey(Y + 1, X + 1)
                else:
                    # Word selection loop
                    fI = 0
                    color = curses.color_pair(Cell.W3)  # Red
                    fWORDS = [(k, *fWORDS[k]) for k in fWORDS]
                    fWORDS.sort(key=lambda x: -x[-1])
                    while True:
                        fW, fJ, fY, fX, fV, fP = fWORDS[fI]
                        for i in range(H):
                            for j in range(W):
                                ch = "*" if TABJ[i][j] else TABLE[i][j]
                                wtable.addstr(i + 1, j + 1, ch)
                        for k in range(len(fW)):
                            i = fY + (k if fV else 0)
                            j = fX + (0 if fV else k)
                            if TABLE[i][j] == " ":
                                ch = "*" if fJ[k] else fW[k]
                                wtable.addstr(i + 1, j + 1, ch, color)
                        wtable.refresh()
                        status("{} ({})".format(fW, fP))

                        k = wtable.getkey(Y + 1, X + 1).upper()
                        if k == "KEY_PPAGE" or k == "KEY_UP" or k == "KEY_LEFT":
                            fI = max(fI - 1, 0)
                        elif k == "KEY_NPAGE" or k == "KEY_DOWN" or k == "KEY_RIGHT":
                            fI = min(fI + 1, len(fWORDS) - 1)
                        elif k == "\n":  # Enter
                            for k in range(len(fW)):
                                i = fY + (k if fV else 0)
                                j = fX + (0 if fV else k)
                                TABLE[i][j] = fW[k]
                                TABJ[i][j] = fJ[k]
                                CARDS = ""
                                wcards.addstr(1, 1 + (WC - lang.NCARDS) // 2, " " * lang.NCARDS)
                                wcards.addstr(1, 1 + (WC - lang.NCARDS) // 2, CARDS)
                                wcards.refresh()
                            break
                        elif k == "0":  # ESC is '\0x1b'
                            break
            # Out of the loop, the table will be updated at the end of the if
            finderkeys(False)
            status("Table input, " + ("vertical" if VERT else "horizontal"))
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
        elif k == "KEY_DC":
            TABLE[Y][X] = " " # DEL
            TABJ[Y][X] = False
        elif k == "\t":
            J = not J
        elif k == "*":
            status("Type the letter the jolly means")
            k = wtable.getkey(Y + 1, X + 1).upper()
            if k in lang.LETTERS and k != "*":
                TABLE[Y][X] = k
                TABJ[Y][X] = True
            status("Table input, " + ("vertical" if VERT else "horizontal"))
            if VERT:
                Y = min(H - 1, Y + 1)
            else:
                X = min(W - 1, X + 1)
        elif k in lang.LETTERS:  # and k != "*"
            TABLE[Y][X] = k
            TABJ[Y][X] = False
            if VERT:
                Y = min(H - 1, Y + 1)
            else:
                X = min(W - 1, X + 1)

        # Update table display, TODO use A_STANDOUT for jollys
        for i in range(H):
            for j in range(W):
                cell = lang.TABLE[i][j]
                cattr = curses.color_pair(cell)
                if TABLE[i][j] == " ":
                    wtable.addstr(i + 1, j + 1, CELL_CH[cell], cattr)
                else:
                    if TABJ[i][j]:
                        cattr |= curses.A_BOLD
                        ch = "*" if J else TABLE[i][j]
                    else:
                        ch = TABLE[i][j]
                    wtable.addstr(i + 1, j + 1, ch, cattr)


curses.wrapper(main)
