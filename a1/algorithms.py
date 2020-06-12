"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithms'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional
from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Precondition:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """
    num_people: int

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new RandomArrivals

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        ArrivalGenerator.__init__(self, max_floor, num_people)
        if num_people is None:
            self.num_people = 0

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """
        Generate a fixed number of new arrivals with random start and target
        floors at the given round. Return the dictionary mapping floor numbers
        to the people who arrived starting at that floor.
        """
        wait_list = {}
        i = 1
        while i <= self.num_people:
            a = random.sample(range(1, self.max_floor + 1), 2)
            if a[0] not in wait_list:
                wait_list[a[0]] = [Person(a[0], a[1])]
            else:
                wait_list[a[0]].append(Person(a[0], a[1]))
            i += 1
        return wait_list


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    ==== Attribute ====
        wait_file: a dictionary mapping floor numbers to the people who
        arrived starting at that floor
    """
    wait_file: Dict[int, List[int]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
            The start floor and target floor in the file should be between 1
            and the maximum floor of the building, inclusive.
        """
        ArrivalGenerator.__init__(self, max_floor, None)
        self.wait_file = {}
        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                # ['1', ' 1', ' 4', ' 5', ' 3']
                # ['3', ' 1', ' 2']
                # ['5', ' 4', ' 2']
                int_line = [int(x) for x in line]
                self.wait_file[int_line[0]] = int_line[1:]

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        wait_list = {}
        people = self.wait_file.get(round_num, [])
        i = 0
        while i < len(people):
            if people[i] not in wait_list:
                wait_list[people[i]] = [Person(people[i], people[i + 1])]
            else:
                wait_list[people[i]].append(Person(people[i], people[i + 1]))
            i = i + 2
        return wait_list


###############################################################################
# Elevator moving algorithms
###############################################################################

class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


# Helper Function


def nobody_waiting(waiting: Dict[int, List[Person]]) -> bool:
    """
    Return True if nobody is waiting for the elevator, and False if someone is
    waiting for the elevator.

    >>> a = Person(1, 2)
    >>> w = {1: [a]}
    >>> nobody_waiting(w)
    False
    >>> ww = {}
    >>> nobody_waiting(ww)
    True
    """
    for floor in waiting:
        if len(waiting[floor]) != 0:
            return False
    # someone waiting
    return True


def get_direction(num1: int, num2: int) -> Direction:
    """
    Return the direction after comparing two numbers, where num1 is the floor
    the elevator is moving to and num2 is the current position of the elevator
    in PushyPassenger algorithm, and in ShortSighted algorithm num1 represents
    the closest distance and num2 is 0.

    num1 and num2 cannot equal since the floor that the elevator is moving to
    and the current position of elevator cannot be the same according to the
    order of the simulation in every round.

    Precondition: num1 != num2

    >>> a = get_direction(2,3)
    >>> b = Direction.DOWN
    >>> a == b
    True
    >>> c = get_direction(-3, 0)
    >>> d = Direction.DOWN
    >>> c == d
    True
    """
    if num1 < num2:
        return Direction.DOWN
    else:
        return Direction.UP


def direction_to_lowest(elevator_position: int,
                        waiting: Dict[int, List[Person]],
                        max_floor: int) -> Direction:
    """
    Return the direction for an elevator to move after comparing the current
    position with the lowest floor, which is calculated by comparing all the
    floors in waiting.

    Precondition:
    1 <= elevator_position <= max_floor
    max_floor >= 2

    >>> Cute_wql = Person(3, 26)
    >>> Beautiful_wyl = Person(10, 24)
    >>> perfect_partner = {3: [Cute_wql], 10: [Beautiful_wyl]}
    >>> a = direction_to_lowest(4, perfect_partner, 26)
    >>> a == Direction.DOWN
    True
    >>> c = direction_to_lowest(2, perfect_partner, 26)
    >>> c == Direction.UP
    True
    """
    lowest = max_floor
    for floor in waiting:
        if floor < lowest and waiting[floor] != []:
            lowest = floor
    return get_direction(lowest, elevator_position)


def direction_to_closet(elevator_position: int,
                        waiting: Dict[int, List[Person]],
                        max_floor: int) -> Direction:
    """
    Return the direction for an elevator to move to after comparing the closest
    distance and 0, where closest distance is the distance between the closest
    floor where there is at least one person waiting and the current position
    of the elevator.

    If closest distance > 0, the elevator should move up, and vice versa.

    >>> a = Person(1, 2)
    >>> b = Person(6, 3)
    >>> w = {1: [a], 6: [b]}
    >>> c = direction_to_closet(2, w, 6)
    >>> c == Direction.DOWN
    True
    >>> e = Person(3, 6)
    >>> w[3] = [e]
    >>> f = direction_to_closet(2, w, 6)
    >>> f == Direction.DOWN
    True
    """
    closest_distance = max_floor - 1
    for floor_num in waiting:
        if abs(floor_num - elevator_position) < abs(
                closest_distance) and waiting[floor_num] != []:
            closest_distance = floor_num - elevator_position
        elif floor_num - elevator_position == -(
                closest_distance) and waiting[floor_num] != []:
            closest_distance = -abs(closest_distance)
    return get_direction(closest_distance, 0)


# Helper


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of random directions for each elevator to move to.
        """
        direction = []
        for elevator in elevators:
            if not (elevator.position == 1 or elevator.position == max_floor):
                direction.append(random.choice(
                    [Direction.DOWN, Direction.STAY, Direction.UP]))
            elif elevator.position == 1:
                direction.append(random.choice([Direction.STAY,
                                                Direction.UP]))
            elif elevator.position == max_floor:
                direction.append(
                    random.choice([Direction.DOWN, Direction.STAY]))
        return direction


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """
        Return a list of directions for elevators to move to based on the
        PushyPassenger algorithm.
        """
        direction = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                if nobody_waiting(waiting):
                    direction.append(Direction.STAY)
                    # stay still as nobody waiting
                else:
                    direction.append(direction_to_lowest(elevator.position,
                                                         waiting, max_floor))
            else:  # assert there is at least one passenger in that elevator
                direction.append(get_direction(elevator.passengers[0].target,
                                               elevator.position))
        return direction


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """
        Return a list of directions for elevators to move to based on the
        PushyPassenger algorithm.
        """
        direction = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                if nobody_waiting(waiting):
                    direction.append(Direction.STAY)
                else:
                    direction.append(
                        direction_to_closet(elevator.position, waiting,
                                            max_floor))
            else:
                closest_distance = max_floor - 1
                for person in elevator.passengers:
                    if abs(person.target - elevator.position) < abs(
                            closest_distance):
                        closest_distance = person.target - elevator.position
                    elif person.target - elevator.position == -(
                            closest_distance):
                        closest_distance = -abs(closest_distance)
                direction.append(get_direction(closest_distance, 0))
        return direction


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
