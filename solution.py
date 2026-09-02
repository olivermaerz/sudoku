
from utils import *


row_units = [cross(r, cols) for r in rows]
#pprint(row_units)

column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# add new two dimensional list for the two diagonals
diag_units = [ [rows[i] + cols[i] for i in range(0, 9)], [rows[i] + cols[8-i] for i in range(0, 9)] ]
#pprint(diag_units)

unitlist = row_units + column_units + square_units + diag_units

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
#pprint(units)

peers = extract_peers(units, boxes)
#pprint(peers)


# Utility functions for Naked Twins
def get_column(box):
    """
    Get the column (int 0-8) for a given box
    """
    return (int(box[1])-1)


def get_row(box):
    """
    Get the row (int 0-8) for a given box
    """
    return (ord(box[0])-65)


def get_square(box):
    """
    Get the square (int 0-8) for a given box
    """
    return( (int((ord(box[0])-65)/3)*3) + int((int(box[1])-1)/3) )


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    out = values.copy()  # copy so we don't mutate values
    for dict_element in boxes:
        # First find boxes with exactly two values
        if (len(values[dict_element]) == 2):
            # the two digits of the naked twin
            two_digits = values[dict_element]
            # Find another box with the same value in peers
            for peer in peers[dict_element]:
                if values[peer] == values[dict_element]:
                    # Peer with same value found !
                    # Now check if it is in the same row ...
                    if get_row(dict_element) == get_row(peer):
                        for row_unit in row_units[get_row(dict_element)]:
                            if (len(values[row_unit]) > 1) and (values[row_unit] != two_digits):
                                out = assign_value(out, row_unit, out[row_unit].replace(two_digits[0],''))
                                out = assign_value(out, row_unit, out[row_unit].replace(two_digits[1],''))
                    # ... if it was not in the same row then check if it is in the same column
                    elif get_column(dict_element) == get_column(peer):
                        for column_unit in column_units[get_column(dict_element)]:
                            if (len(values[column_unit]) > 1) and (values[column_unit] != two_digits):
                                out = assign_value(out, column_unit, out[column_unit].replace(two_digits[0],''))
                                out = assign_value(out, column_unit, out[column_unit].replace(two_digits[1],''))
                    # and finally check if it is the same square
                    if get_square(dict_element) == get_square(peer):
                        for square_unit in square_units[get_square(dict_element)]:
                            if (len(values[square_unit]) > 1) and (values[square_unit] != two_digits):
                                out = assign_value(out, square_unit, out[square_unit].replace(two_digits[0],''))
                                out = assign_value(out, square_unit, out[square_unit].replace(two_digits[1],''))
    return out


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for dict_element in values.keys():
        if len(values[dict_element]) <= 1:
            # element has just one digit
            for peer in peers[dict_element]:
                # values[peer] = values[peer].replace(values[dict_element],'')
                values = assign_value(values, peer, values[peer].replace(values[dict_element],''))
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        # call the naked twins strategy 
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = reduce_puzzle(values)
    values = search(values)

    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
