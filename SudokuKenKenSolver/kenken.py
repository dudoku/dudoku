from z3 import *
import sys


# Get input

# Solves the kenken puzzle.
# n is the dimension of the grid
def solve_puzzle(n, puzzle):
    # Declare the grid for Z3
    grid = [[Int("X{0}_{1}".format(i, j)) for i in range(n)] for j in range(n)]

    # Create a solver instance for Z3
    s = Solver()

    # Add constraint that each cage meets its goal
    for sublist in puzzle:
        goal = sublist[0]
        operation = sublist[1]
        if operation == '+':
            sum = 0
            for v in range(1, (len(sublist) - 2) / 2 + 1):
                sum += grid[sublist[2*v]][sublist[2*v+1]]
            s.add(goal == sum)
        elif operation == '*':
            prod = 1
            for v in range(1, (len(sublist) - 2) / 2 + 1):
                prod *= grid[sublist[2 * v]][sublist[2 * v + 1]]
            s.add(goal == prod)
        elif operation == '-':
            a = grid[sublist[2]][sublist[3]]
            b = grid[sublist[4]][sublist[5]]
            s.add(Or(a - b == goal, b - a == goal))
        elif operation == '/':
            a = grid[sublist[2]][sublist[3]]
            b = grid[sublist[4]][sublist[5]]
            s.add(Or(a/b == goal, b/a == goal))
        elif operation == 'g':
            s.add(grid[sublist[2]][sublist[3]] == goal)

    # Add constraint that each cell is in [1,n]
    for i in range(n):
        for j in range(n):
            s.add(And(1 <= grid[i][j], grid[i][j] <= n))

    # Add rule for rows having distinct values
    for r in range(n):
        s.add(Distinct([grid[r][c] for c in range(n)]))

    # Add rule for columns being distinct
    for c in range(n):
        s.add(Distinct([grid[r][c] for r in range(n)]))

    # Check if Z3 can solve the puzzle
    if s.check() == sat:
        # Get Z3's solution
        m = s.model()
        # Extract the solution into a python matrix
        solution = [[0 for i in range(n)] for j in range(n)]
        for i in range(n):
            for j in range(n):
                solution[i][j] = int(str(m.eval(grid[i][j])))

        # Print solution
        for i in range(n):
            row = ""
            for j in range(n):
                row = row + str(solution[i][j]) + " "
            print(row)

    else:
        print("No solution")

OPS = ['+', '-', '*', '/', 'g']

#Main method given: MSB
if __name__ == '__main__':
    if len(sys.argv) == 1:
        n = 6

        puzzle = [[11, '+', 0, 0, 1, 0],
                  [2, '/', 0, 1, 0, 2],
                  [3, '-', 1, 1, 1, 2],
                  [20, '*', 0, 3, 1, 3],
                  [6, '*', 0, 4, 0, 5, 1, 5, 2, 5],
                  [3, '/', 1, 4, 2, 4],
                  [240, '*', 2, 0, 2, 1, 3, 0, 3, 1],
                  [6, '*', 2, 2, 2, 3],
                  [6, '*', 3, 2, 4, 2],
                  [7, '+', 3, 3, 4, 3, 4, 4],
                  [30, '*', 3, 4, 3, 5],
                  [6, '*', 4, 0, 4, 1],
                  [9, '+', 4, 5, 5, 5],
                  [8, '+', 5, 0, 5, 1, 5, 2],
                  [2, '/', 5, 3, 5, 4]]
        solve_puzzle(n, puzzle)
    else:
        # haphazard data parsing
        # * doesn't check for correct format

        # grab data and get out
        with open(sys.argv[1], 'r') as f:
            lines = [line.strip() for line in f]

        # remove blank lines
        lines = filter(lambda x: x != "", lines)

        # get n
        n = int(lines[0])

        # split rest of the lines
        lines = map(lambda x: x.split(), lines[1:])

        # cast strings to ints, except for OPS
        for i in range(len(lines)):
            lines[i] = map(lambda item: item if item in OPS else int(item), lines[i])

        solve_puzzle(n, lines)