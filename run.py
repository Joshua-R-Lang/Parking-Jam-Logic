
from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"


from examples import generate_board
example1 = generate_board()


# Encoding that will store all of your constraints
E = Encoding()

CAR_ORIENTATIONS = [0, 1] #0 for NS, 1 for EW


LOCATIONS = []
LOCATION_GRID = {}

class Car:
    def __init__(self, car_id, x, y, orientation):
        """
        Initialize a car with a unique ID, starting position, and orientation.
        orientation: 0 for vertical (up/down), 1 for horizontal (right/left)
        """
        self.car_id = car_id
        self.x = x
        self.y = y
        self.orientation = orientation  # 0 for vertical, 1 for horizontal

   def possible_moves(self, grid, barriers):
        """
        Generate all possible moves for the car within the grid, considering barriers and other cars.
        """
        moves = []
        if self.orientation == 1:  # Horizontal car moves left or right
            if self.can_move(grid, barriers, dx=1):
                moves.append((self.x + 1, self.y))  # Move right
            if self.can_move(grid, barriers, dx=-1):
                moves.append((self.x - 1, self.y))  # Move left
        else:  # Vertical car moves up or down
            if self.can_move(grid, barriers, dy=1):
                moves.append((self.x, self.y + 1))  # Move down
            if self.can_move(grid, barriers, dy=-1):
                moves.append((self.x, self.y - 1))  # Move up
        return moves

    def can_move(self, grid, barriers, dx=0, dy=0):
        """
        Check if the car can move in the given direction (dx, dy) without hitting boundaries, other cars, or barriers.
        """
        new_x = self.x + dx
        new_y = self.y + dy
        # Check grid boundaries
        if not (0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid)):
            return False
        # Check if cell is empty and not a barrier
        if grid[new_y][new_x] == 0 and (new_x, new_y) not in barriers:
            return True
        return False


class Barrier:
    def __init__(self, x, y):
        """
        Initialize a barrier at a specified (x, y) position.
        """
        self.x = x
        self.y = y

    def position(self):
        """
        Return the position of the barrier as a tuple.
        """
        return (self.x, self.y)

def set_exit(self, x, y):
    """
    Define the exit position where cars can leave the grid.
    """
    self.exit_position = (x, y)


def generate_locations(rows=4, cols=4):
    global LOCATIONS, LOCATION_GRID
    
    for row in range(1, rows + 1):
        LOCATION_GRID[row] = {}
        for col in range(1, cols + 1):
            location_id = f'l{row}{col}'
            LOCATIONS.append(location_id)
            LOCATION_GRID[row][col] = location_id

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")   
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
