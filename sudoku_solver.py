from z3 import *
import sys

# Get input

# Solves the sudoku puzzle.
# n is the length of a sub-grid and puzzle is the provided puzzle
def solve_puzzle(n, puzzle):
    # Declare the grid for Z3
    grid = [[Int("X{0}_{1}".format(i, j)) for i in range(n * n)] for j in range(n * n)]

    # Create a solver instance for Z3
    s = Solver()

    # Add constraint that each cell is in [1,n*n]
    for i in range(n * n):
        for j in range(n * n):
            s.add(And(1 <= grid[i][j], grid[i][j] <= n * n))

    # Add rule for rows having distinct values
    for r in range(n * n):
        s.add(Distinct([grid[r][c] for c in range(n * n)]))

    # Add rule for columns being distinct
    for c in range(n * n):
        s.add(Distinct([grid[r][c] for r in range(n * n)]))

    # Add rule for boxes being distinct
    for i in range(n):
        for j in range(n):
            s.add(Distinct([grid[r][c] for c in range(i * n, i * n + n) for r in range(j * n, j * n + n)]))

    # Give Z3 our puzzle
    for i in range(n * n):
        for j in range(n * n):
            # Skip if this is a blank square
            if puzzle[i][j] == ".":
                continue
            # Otherwise, add a constraint that this
            # square == the puzzle square
            s.add(grid[i][j] == puzzle[i][j])

    # Check if Z3 can solve the puzzle
    if s.check() == sat:
        # Get Z3's solution
        m = s.model()
        # Extract the solution into a python matrix
        solution = [[0 for i in range(n * n)] for j in range(n * n)]
        for i in range(n * n):
            for j in range(n * n):
                solution[i][j] = int(str(m.eval(grid[i][j])))

        # Print solution
        for i in range(n * n):
            row = ""
            for j in range(n * n):
                row = row + str(solution[i][j]) + " "
            print(row)

        """
        # Create constraint for one empty cell having a different value
        # Check if solution is not unique
        for i in range(n * n):
            for j in range(n * n):
                # Check the blank square
                if puzzle[i][j] == ".":
                    # list of 1-9, remove solution[i][j], because want to solve with a value other than
                    # the one in the solution
                    aList = []
                    for u in range(1, n*n):
                        if u != solution[i][j]:
                            aList.append(u)
                    # Or() makes sure at least one is true, (takes multiple arguments or list)
                    s.add(Or([grid[i][j] == aList[t] for t in range (0, len(aList))]))

                    #There exists a square that is not equal to the square of the given solution
                    if s.check() == sat:
                        print("The solution is not unique")
                        return
        print("The solution is unique")
        """
    else:
        print("No solution")


if __name__ == '__main__':
    if len(sys.argv) != 1:
        # grab data and get out
        with open(sys.argv[1]) as f:
            lines = [line.strip() for line in f]

        # remove empty lines
        lines = filter(lambda x: x != "", lines)

        # get dim
        n = int(lines[0])

        # split lines
        lines = [line.split() for line in lines[1:]]

        # cast ints
        for i in range(len(lines)):
            lines[i] = map(lambda x: x if x == '.' else int(x), lines[i])

        # call solver
        solve_puzzle(n, lines)
    else:
        print("Takes in a single file as input.")