**Some more optimization can definitely still be done, but I am not moving on with this.**

# SudokuSolver
A sudoku-solving script implemented in pure Python 3 (only standard modules are
used).

# ScrabbleSolver
A scrabble best-word finder implemented in pure Python 3 (only standard modules
are used, with the small caveats below).

The program uses the `curses` module and therefore will not be able to run under
Windows unless you use Cygwin, MinGW or WSL. It also assumes your terminal
supports minimal colors.

The program also assumes that a dictionary for the appropriate language is
present in `/usr/share/dict`, shuch as `/usr/share/dict/italian` for the `it`
version, etc. The dictionary should provide a list of words, one per line, as
those provided by the `w*` Debian packages (`witalian`, etc.).
