#!/usr/bin/env python3
# Representing a sudoku as a list of lists, the first index being the row and
# the second being the column (C-ordering, we have a list of rows which are
# lists of ints). 0 represents an empty cell (to-be-filled).
# 3x3 boxes are numbered by row (the top-left is k=0, the top-right is k=2, ...,
# the bottom-left is k=6 and the bottom-right is k=8).
from copy import deepcopy


def int_cell(x):
    """Convert a char to a cell representation. Raises exceptions on failure."""
    if len(x) != 1:
        raise ValueError("Not a char!")
    return 0 if x == " " else int(x)


def sudoku_input():
    """User input to sudoku grid representation. Returns None on failure."""
    rows = []
    for i in range(9):
        row = input()
        if len(row) > 9:
            return None
        row += " " * (9 - len(row))
        try:
            row = [int_cell(x) for x in row]
        except Exception:
            return None
        rows.append(row)
    return rows


def sudoku_print(grid):
    """Prints the grid in a readable form."""
    for i in range(9):
        print("|".join(
            "".join(str(grid[i][j]) for j in range(3 * n, 3 * n + 3))
            for n in range(3)
        ))
        if i % 3 == 2 and i // 3 < 2:
            print("---+---+---")


def get_row_missing(grid, i):
    """Returns a set of the numbers to be filled in the i-th row of grid."""
    return set(x + 1 for x in range(9)) - set(grid[i])


def get_col_missing(grid, j):
    """Returns a set of the numbers to be filled in the j-th column of grid."""
    return set(x + 1 for x in range(9)) - set(r[j] for r in grid)


def box_iter(grid, k):
    """Iterates through the elements of the k-th box of grid."""
    br, bc = divmod(k, 3)
    for i in range(3 * br, 3 * br + 3):
        for j in range(3 * bc, 3 * bc + 3):
            yield grid[i][j]


def get_box_missing(grid, k):
    """Returns a set of the numbers to be filled in the k-th box of grid."""
    return set(x + 1 for x in range(9)) - set(x for x in box_iter(grid, k))


def get_box_index(i, j):
    """Returns the index k of the box the cell (i, j) belongs to."""
    return (i // 3) * 3 + (j // 3)


def fill_unique(grid):
    """
    Fills cells that have only one possibility in-place. Returns number of cells
    filled. Returns -1 if a cell has no possible value.
    """
    n = 0
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                continue  # Cell content already fixed
            possib = get_row_missing(grid, i)
            possib &= get_col_missing(grid, j)
            possib &= get_box_missing(grid, get_box_index(i, j))
            if len(possib) == 0:
                return -1
            if len(possib) == 1:
                n += 1
                grid[i][j] = possib.pop()
    return n


def get_status(grid):
    """
    Returns 0 if the grid is yet to be solved, 1 if the grid is solved and -1 if
    the grid is not solvable (i.e. contains errors).
    """
    res = 1
    for i in range(9):  # Check rows
        rowstat = [0] * 10
        for j in range(9):
            rowstat[grid[i][j]] += 1
        if any(n > 1 for n in rowstat[1:]):
            return -1  # Error(s)
        if rowstat[0] > 0:
            res = 0  # Empty cells
    for j in range(9):  # Check cols
        colstat = [0] * 10
        for i in range(9):
            colstat[grid[i][j]] += 1
        if any(n > 1 for n in colstat[1:]):
            return -1  # Error(s)
        if colstat[0] > 0:
            res = 0  # Empty cells
    for k in range(9):  # Check boxes
        boxstat = [0] * 10
        for x in box_iter(grid, k):
            boxstat[x] += 1
        if any(n > 1 for n in boxstat[1:]):
            return -1  # Error(s)
        if boxstat[0] > 0:
            res = 0  # Empty cells
    return res


def brute_force(grid):
    """Find a cell with multiple possible values and try them all."""
    # When brute_force is called, grid has no empty cell with len(possib) <= 1
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                continue  # Cell content already fixed
            possib = get_row_missing(grid, i)
            possib &= get_col_missing(grid, j)
            possib &= get_box_missing(grid, get_box_index(i, j))
            for p in possib:
                grid[i][j] = p  # No need to preserve grid at this point
                yield from recursive_solve(grid)
            return  # Only test one cell, recursive_solve will do the rest


def recursive_solve(grid):
    """Yields all solutions for a certain grid."""
    grid = deepcopy(grid)  # Avoid modifying the original
    # First fill all the cells that have only one possible number
    while True:
        n = fill_unique(grid)
        if n == 0:
            break
        if n == -1:
            return  # One cell has no possible number, no solution here
    # Check if the grid is solved
    s = get_status(grid)
    if s == -1:
        return  # Grid has errors, no solution here
    if s == 1:
        yield grid  # Grid is solved
        return  # Done here
    # If the grid is still not solved go with bruteforce algorithm
    yield from brute_force(grid)


# Prompt the user to enter a sudoku to be solved
print("Enter the sudoku grid to be solved as 9 lines of 9 numbers. An empty")
print('box can be entered as either a "0" (zero) or a " " (space). Do not use')
print("any character to split 3x3 boxes, rows or columns.")
while True:
    print()
    grid = sudoku_input()
    print()
    if grid is not None:
        break
    print("Please enter something like the part on the left (the part on the")
    print("right is a more readable representation):")
    print("   3 5                        |3 5|   ")
    print("  98 23                      9|8 2|3  ")
    print(" 5     9                    5 |   | 9 ")
    print("82     31                  ---+---+---")
    print("                 =>        82 |   | 31")
    print("46     87                     |   |   ")
    print(" 8     6                   46 | 1 | 87")
    print("  32 15                    ---+---+---")
    print("   7 4                      8 |   | 6 ")
    print("                             3|2 1|5  ")
    print("                              |724|   ")


print("Solving...")
n = 0
for sol in recursive_solve(grid):
    n += 1
    print()
    sudoku_print(sol)
print()
print("{} solutions found.".format(n))
