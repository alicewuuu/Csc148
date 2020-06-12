"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any
import algorithms
from entities import Person, Elevator
from visualizer import Visualizer

# Helper Function


def get_passengers(elevator: Elevator) -> List[Person]:
    """
    Return a list of passengers for a given elevator.

    >>> a = Elevator(2)
    >>> get_passengers(a)
    []
    >>> Cute_wang = Person(2,3)
    >>> Beautiful_wu = Person(3,4)
    >>> a.passengers.append(Cute_wang)
    >>> a.passengers.append(Beautiful_wu)
    >>> b = get_passengers(a)
    >>> c = [Cute_wang, Beautiful_wu]
    >>> b == c
    True
    """
    list_passengers = []
    # copy a list of passenger from the elevator
    for person in elevator.passengers:
        list_passengers.append(person)
    return list_passengers

# Helper Function


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the PyGame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
    (keys are floor numbers, values are the list of waiting people)
    iterations: the total number of the number of simulation rounds that
    took place
    total_people: the total number of people in a simulation
    completed_people: the number of people who reached their target
    destination by the end of the simulation
    waiting_time: a list of time someone spent before reaching their target
    floor during the simulation

    === Representation Invariants ===
    num_floors >= 2
    iterations >= 0
    total_people >= 0
    len(elevators) >= 1
    completed_people >= 0
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    iterations: int
    total_people: int
    completed_people: int
    waiting_time: List[int]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration.

        Precondition:
            config['num_floors'] >= 2
            config['num_elevators'] >= 1
            config['elevator_capacity'] >= 1
            config['num_people_per_round'] >= 0
        """

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.arrival_generator = config['arrival_generator']
        elevator = []
        while len(elevator) != config['num_elevators']:
            elevator.append(Elevator(config['elevator_capacity']))
        self.elevators = elevator
        self.moving_algorithm = config['moving_algorithm']
        self.num_floors = config['num_floors']
        self.waiting = {}
        self.iterations = 0
        self.total_people = 0
        self.completed_people = 0
        self.waiting_time = []
        self.visualizer = Visualizer(self.elevators, self.num_floors,
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)
            self.iterations += 1

        return self._calculate_stats()

    def _update_wait_time(self) -> None:
        """
        Update the wait_time of person in the waiting list.
        """
        if self.waiting != {}:
            for i in self.waiting:
                for person in self.waiting[i]:
                    person.wait_time += 1

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        update_list = self.arrival_generator.generate(round_num)
        self._update_wait_time()
        for floor_num in update_list:
            self.total_people += len(update_list[floor_num])
            if floor_num not in self.waiting:
                self.waiting[floor_num] = update_list[floor_num]
            else:
                for person in update_list[floor_num]:
                    self.waiting[floor_num].append(person)
        self.visualizer.show_arrivals(update_list)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            passengers = get_passengers(elevator)
            # copy a list of passenger in that elevator to passengers
            for person in passengers:
                if elevator.position == person.target:
                    # statistic data
                    self.waiting_time.append(person.wait_time)
                    elevator.passengers.remove(person)
                    self.visualizer.show_disembarking(person, elevator)
                    # statistic data
                    self.completed_people += 1

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            if elevator.position in self.waiting:
                people = self.waiting[elevator.position]
                while elevator.fullness() < 1 and not people == []:
                    p = people[0]
                    elevator.boarding(p)
                    self.visualizer.show_boarding(p, elevator)
                    people.remove(p)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        moving = self.moving_algorithm.move_elevators(self.elevators,
                                                      self.waiting,
                                                      self.num_floors)
        for i in range(len(self.elevators)):
            self.elevators[i].position += moving[i].value
            for passenger in self.elevators[i].passengers:
                passenger.wait_time += 1
        self.visualizer.show_elevator_moves(self.elevators, moving)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        if len(self.waiting_time) != 0:
            max_t = max(self.waiting_time)
            min_t = min(self.waiting_time)
            avg_t = int(sum(self.waiting_time) / len(self.waiting_time))
        else:
            max_t = min_t = avg_t = -1
        return {
            'num_iterations': self.iterations,
            'total_people': self.total_people,
            'people_completed': self.completed_people,
            'max_time': max_t,
            'min_time': min_t,
            'avg_time': avg_t
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': 5,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.RandomArrivals(6, 2),
        'moving_algorithm': algorithms.RandomAlgorithm(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'disable': ['R0201'],
        'max-attributes': 12,
        'max-nested-blocks': 4
    })
