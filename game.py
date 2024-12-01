from lib204 import Encoding, proposition, constraint



# Initialize encoding
E = Encoding()

@proposition(E)
class CarPosition:
    def __init__(self, car_id, x, y):
        self.car_id = car_id
        self.x = x
        self.y = y

    def _prop_name(self):
        return f"Car({self.car_id},{self.x},{self.y})"


@proposition(E)
class CarEscape:
    def __init__(self, car_id):
        self.car_id = car_id

    def _prop_name(self):
        return f"Escape({self.car_id})"


@proposition(E)
class BlockedState:
    def __init__(self, car_id):
        self.car_id = car_id

    def _prop_name(self):
        return f"Blocked({self.car_id})"


@proposition(E)
class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def _prop_name(self):
        return f"Barrier({self.x},{self.y})"


class Car:
    def __init__(self, car_id, x, y, orientation):
        self.car_id = car_id
        self.x = x
        self.y = y
        self.orientation = orientation  # 1 for horizontal, 0 for vertical

    def __repr__(self):
        return f"Car({self.car_id}, x={self.x}, y={self.y}, orientation={'Horizontal' if self.orientation else 'Vertical'})"


def define_movement_constraints(grid_size, cars, barriers):
    """
    Define movement constraints for cars based on their orientation.
    """
    for car in cars:
        if car.orientation == 1:  # Horizontal car
            # Check the row for escape paths
            left_clear = constraint.And([~Barrier(x, car.y) for x in range(0, car.x)])
            right_clear = constraint.And([~Barrier(x, car.y) for x in range(car.x + 1, grid_size)])
            E.add_constraint(CarEscape(car.car_id) >> (left_clear | right_clear))

            # Blocking constraints
            left_blocked = constraint.Or([CarPosition(blocking_car.car_id, x, car.y)
                                          for blocking_car in cars if blocking_car != car
                                          for x in range(0, car.x)])
            right_blocked = constraint.Or([CarPosition(blocking_car.car_id, x, car.y)
                                           for blocking_car in cars if blocking_car != car
                                           for x in range(car.x + 1, grid_size)])
            E.add_constraint(BlockedState(car.car_id) >> (left_blocked & right_blocked))

        else:  # Vertical car
            # Check the column for escape paths
            up_clear = constraint.And([~Barrier(car.x, y) for y in range(0, car.y)])
            down_clear = constraint.And([~Barrier(car.x, y) for y in range(car.y + 1, grid_size)])
            E.add_constraint(CarEscape(car.car_id) >> (up_clear | down_clear))

            # Blocking constraints
            up_blocked = constraint.Or([CarPosition(blocking_car.car_id, car.x, y)
                                        for blocking_car in cars if blocking_car != car
                                        for y in range(0, car.y)])
            down_blocked = constraint.Or([CarPosition(blocking_car.car_id, car.x, y)
                                          for blocking_car in cars if blocking_car != car
                                          for y in range(car.y + 1, grid_size)])
            E.add_constraint(BlockedState(car.car_id) >> (up_blocked & down_blocked))


def is_winnable(cars):
    """
    Add constraints for determining if the game state is winnable.
    """
    # The game is winnable if all cars can escape
    E.add_constraint(constraint.And([CarEscape(car.car_id) for car in cars]))

    # The game is losing if any car is blocked on both sides
    E.add_constraint(~constraint.Or([BlockedState(car.car_id) for car in cars]))


def display_grid(grid, cars, barriers):
    """
    Display the grid with car and barrier positions.
    """
    for y in range(len(grid)):
        row = []
        for x in range(len(grid[0])):
            if any(c.x == x and c.y == y for c in cars):
                row.append("C")
            elif any(b.x == x and b.y == y for b in barriers):
                row.append("B")
            else:
                row.append(".")
        print(" ".join(row))
    print()


def generate_random_board(size=4, num_cars=3, num_barriers=2):
    """
    Generate a random board with cars and barriers.
    """
    grid = [[0 for _ in range(size)] for _ in range(size)]
    cars = []
    barriers = []

    # Add cars
    for car_id in range(1, num_cars + 1):
        while True:
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            orientation = random.choice([0, 1])  # 0 for vertical, 1 for horizontal
            if grid[y][x] == 0:  # Empty cell
                grid[y][x] = car_id
                cars.append(Car(car_id, x, y, orientation))
                break

    # Add barriers
    for _ in range(num_barriers):
        while True:
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            if grid[y][x] == 0:  # Empty cell
                grid[y][x] = -1
                barriers.append(Barrier(x, y))
                break

    return grid, cars, barriers


if __name__ == "__main__":
    import random

    # Define grid size
    grid_size = 4

    # Generate random board
    grid, cars, barriers = generate_random_board(size=grid_size, num_cars=3, num_barriers=2)

    # Display the initial grid
    print("Initial Grid:")
    display_grid(grid, cars, barriers)

    # Define movement constraints
    define_movement_constraints(grid_size, cars, barriers)

    # Add winnability constraints
    is_winnable(cars)

    # Compile encoding
    T = E.compile()

    # Check satisfiability
    print("Satisfiable:", T.satisfiable())
    print("Number of solutions:", count_solutions(T))
    print("Solution:", T.solve())