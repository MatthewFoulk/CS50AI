import sys

from crossword import *
from collections import deque
from copy import deepcopy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            # Need copy otherwise set could change size during iteration
            domainCopy = self.domains[variable].copy()
            variableLen = variable.length
            for word in domainCopy:
                # Word is too long or short crossword spot,
                # so remove it from the domain
                if len(word) != variableLen:
                    self.domains[variable].remove(word)
            


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        wordsToRemove = []

        if overlap is None:
        # No overlaps, so x and y's domains do NOT depend
        # on each other and no changes were made
            return revised

        for xWord in self.domains[x]:
            revisionNeeded = True
            for yWord in self.domains[y]:
                if (xWord != yWord and 
                    xWord[overlap[0]] == yWord[overlap[1]]):
                # There's at least one word from y's domain
                # that fits with this xWord, so no need to remove
                    revisionNeeded = False
                    break
            if revisionNeeded:
            # No word from y's domain fit with this xWord.
            # so it's removed
                wordsToRemove.append(xWord)

        for word in wordsToRemove:      
            self.domains[x].remove(word)
            revised = True

        return revised
                    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.

        NOTE: Deque used for queue due to cost of using a list
        """

        if arcs is None:
        # If `arcs` is None,initialize queue with all 
        # overlaps (removing the ones with "None" overlaps)
            queue = deque([variable
                        for variable in self.crossword.overlaps
                        if self.crossword.overlaps[variable] != None])
        else:
            queue = deque(arcs)

        # While items still in queue
        while len(queue) > 0:
            x, y = queue.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                # Failed to find a solution
                    return False
                for neighbor in self.crossword.neighbors(x):
                # Add all neighbors of x to the queue again
                # except for 'y' because we just revised the
                # domain with respect to 'y'
                    if neighbor != y:
                        queue.appendleft((neighbor, x))
                        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.crossword.variables):
            return False

        for word in assignment.values():
            if word == None:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Verify that every assignment is unique
        if len(assignment) != len(set(assignment.values())):
            return False

        for variable in assignment:

            # Verify that every assignment is the correct length
            if len(assignment[variable]) != variable.length:
                return False

            # Verify that every assignment satisfies the overlap constraint
            for neighbor in self.crossword.neighbors(variable):
                overlap = self.crossword.overlaps[variable, neighbor]
                if neighbor in assignment:
                    if (assignment[variable][overlap[0]] != 
                        assignment[neighbor][overlap[1]]):
                        return False
        return True                

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # order_domain_values = {key: None for key in self.domains[var]}

        # for word in self.domains[var]:
        #     reductions = 0
        #     for neighbor in self.crossword.neighbors(var):

        return self.domains[var]



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # TODO
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        failure = False
        variable = self.select_unassigned_variable(assignment)
        domainCopy = deepcopy(self.domains[variable])

        for word in domainCopy:
            assignment[variable] = word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != failure:
                    return result
                assignment[variable] = None
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
