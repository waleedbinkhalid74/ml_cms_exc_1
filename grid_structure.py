import csv
from enum import Enum
from pathlib import Path
from random import seed

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as spi
from matplotlib import colors


class CellType(Enum):
    """
    Enum Class used to assign cells the 4 types that they can be of.
    """
    EMPTY = 0
    PEDESTRIAN = 1
    OBSTACLE = 2
    TARGET = 3


class Cell:
    """
    Cell class represents one cell in the grid. A cell can be a target, an obstacle, a pedestrian
    (if occupied by a pedestrian) or empty.
    """

    def __init__(self, row: int, col: int, cell_type: CellType = CellType.EMPTY,
                 obstacle_avoidance: bool = True):
        """
        Initiate the cell with the given position to an empty cell
        :param row: represents the cell position in the y-axis
        :param col: represents the cell position in the x-axis
        :param cell_type: the type of the cell
        :param obstacle_avoidance: if false, obstacles are ignored
        """
        super().__init__()
        self.row: int = row
        self.col: int = col
        self.cell_type: CellType = cell_type

        # If obstacle avoidance is True then the obstacle cells have a very high (inf) cost
        # (given in distance_to_target) otherwise they have the same cost.
        if obstacle_avoidance:
            self.distance_to_target: float = np.inf \
                if self.cell_type.value == CellType.OBSTACLE.value else 0
        else:
            self.distance_to_target: float = 0

        # Neighbours are divided into straight and diagonal to take care of distances.
        self.straight_neighbours: list = []
        self.diagonal_neighbours: list = []
        self.dijkstra_cost: float = 0 if self.cell_type.value == CellType.TARGET.value else np.inf

        # This attribute is used to plot the trajectory of pedestrians.
        self.path: bool = False

    def get_distance(self, other_cell, obstacle_avoidance: bool = True) -> float:
        """
        get distance to another cell if the cell is not of type obstacle.
        :param other_cell: cell from which distance has to be calculated
        :param obstacle_avoidance: if false ignores all obstacles
        :return: euclidean distance as a float
        """

        if obstacle_avoidance and self.cell_type.value == CellType.OBSTACLE.value:
            return np.inf
        else:
            return np.sqrt(np.power(self.row - other_cell.row, 2) + np.power(self.col - other_cell.col, 2))

    def cost_to_pedestrian(self, ped, r_max: float = 1.5) -> float:
        """
        get cost added by a pedestrian to a cell based on the repulsion cost function.

        :param ped: A pedestrian with respect to whom to calculate the distance cost
        :param r_max: Maximum distance to start avoiding other pedestrians
        :return: the cost calculated based on the distance to the pedestrian
        """
        r: float = self.get_distance(ped.cell)
        if r >= r_max:
            return 0
        else:
            # return np.exp(1 / (r * r - r_max * r_max))
            return 1 / np.exp(r * r - r_max * r_max)

    def check_if_neighbour_is_target(self) -> bool:
        """
        Checks if the neighbours of a cell are a target.
        :return: True if a target is the neighbour otherwise False
        """
        for neighbour in self.straight_neighbours:
            if neighbour.cell_type.value == CellType.TARGET.value:
                return True
        for neighbour in self.diagonal_neighbours:
            if neighbour.cell_type.value == CellType.TARGET.value:
                return True
        return False

    def __str__(self):
        """
        :return: cell coordinates and the cell type as a String
        """
        return f"Cell ({self.row}, {self.col}) Type = {self.cell_type}"

    def __eq__(self, other_cell):
        """
        Compares if two cells are the same.
        :param other_cell: Cell Type object
        :return: True if cells are the same else false
        """
        return self.row == other_cell.row and self.col == other_cell.col

    def __ge__(self, other_cell):
        """
        Compares if a certain cell is closer to the target compared to another
        :param other_cell: Cell Type object
        :return: True if invoking cells is closer to target than the other cell
        """
        return self.distance_to_target >= other_cell.distance_to_target


class Pedestrian:
    """
    A Pedestrian has a unique cell and a unique id.
    The cell is updated after every step based on a utility function.
    """
    _id_counter: int = 0

    def __init__(self, cell: Cell, speed: float = 1.33, age: int = 20):
        """
        Initiate the pedestrian with the given position & a unique id.
        :param cell: represents the cell where the pedestrian is standing
        :param speed: represents the speed this pedestrian moves in meter/second
        :param age: represents the age of the pedestrian. This can be used to assign the pedestrian a speed based on the
                    age speed diagram in RiMEA figure 2
        row & col in a pedestrian serve to store partial step
            this helps creating more accurate diagonal speed
        delay is the inverse of the speed
            i.e. the time the pedestrian needs to pass one meter in millisecond
        """
        super().__init__()
        Pedestrian._id_counter += 1
        self.id: int = Pedestrian._id_counter  # ID Unique to each pedestrian
        self.cell: Cell = cell  # The cell a pedestrian occupies
        self.age: int = age  # age of the pedestrian
        self.row: float = 0
        self.col: float = 0
        self.speed: float = speed
        self.delay: int = 1000.0 // speed
        self.steps: int = 0
        self.last_move: int = 0  # Time when the last step was made
        self.last_10_steps = []  # Stores the last 10 cells visited along with the time at which they were visited
        # to calculate pedestrian speed

    def is_valid(self) -> bool:
        """
        Checks that the cell where the pedestrian is standing is a pedestrian cell.
        :return: true or false
        """
        return self.cell.cell_type.value == CellType.PEDESTRIAN.value

    def update_cell(self, new_cell: Cell):
        """
        Set the current cell to empty and assign the pedestrian's cell the new cell.
        Add the new cell to the pedestrian path and save the update in last_10_steps
        for future measurements.
        :param new_cell: The cell to move to
        :return: None
        """
        self.cell.cell_type = CellType.EMPTY
        self.cell.path = True
        if len(self.last_10_steps) >= 10:
            self.last_10_steps.pop(0)
        self.cell = new_cell

    def move(self, cell: Cell, constant_speed: bool = True,
             current_time: int = 0, max_steps: int = 1000,
             cell_scale: float = 0.4) -> (float, float, bool):
        """
        Checks if the pedestrian is maintaining their speed. If so then checks if a diagonal step is made or a straight step.
        A straight step is straight forward but if it is a diagonal step then movements potentials are accumulated
        and if they are more than 1 then the diagonal move can be made.
        :param constant_speed: A flag indicating whether the speed is constant or individual to pedestrians
        :param cell_scale: cell dimension in meter
        :param max_steps: Maximum number of allow steps
        :param current_time: Time passed since the beginning of simulation in millisecond
        :param cell: The cell where the pedestrian needs to move
        :return: a pair of float indicating the distance &
            direction the pedestrian should move and a bool stating is the move is diagonal or not
        """
        cell_delay = self.delay * cell_scale
        if constant_speed or \
                (current_time > self.last_move + cell_delay and self.steps <= max_steps):
            self.last_move = current_time
            self.last_10_steps.append([self.cell, self.delay * self.steps])
            self.steps += 1
            if self.cell.row != cell.row and self.cell.col != cell.col:
                # diagonal step
                # the pedestrian only moves 0.7 horizontally & vertically
                full_row = self.row + (cell.row - self.cell.row) * 0.71
                full_col = self.col + (cell.col - self.cell.col) * 0.71
                # remove the potential 1 from self.row & self.col keeping the sign
                #   if a diagonal step can be made
                if np.abs(full_row) >= 1 and np.abs(full_col) >= 1:
                    self.row = (full_row % 1.0) * np.sign(full_row)
                    self.col = (full_col % 1.0) * np.sign(full_col)
                else:
                    # if not accumulate the diagonal potential
                    self.row = full_row
                    self.col = full_col
                return full_row, full_col, True
            else:
                # straight step, also return false to indicate that a diagonal step was not made
                return (cell.row - self.cell.row), (cell.col - self.cell.col), False
        else:
            return 0, 0, False

    def measure_speed(self, cell_scale: float = 0.4):
        """
        Pedestrian class function that measures the speed of the pedestrain considering its last_steps steps
        :param cell_scale: The size of cell in meters
        :return: The average speed over the last_steps in meter/second
        """
        # measure the covered distance by last_steps
        # Scale the distance according to cell_scale
        # get the speed by dividing distance / (last_time - first_time)

        distance = 0
        last_steps = np.array(self.last_10_steps)
        if len(last_steps) <= 2:
            return 0
        initial_time = last_steps[0, 1]
        final_time = last_steps[-1, 1]
        first_cell = last_steps[0, 0]
        time = (final_time - initial_time) * cell_scale
        for step in range(1, len(last_steps)):
            if last_steps[step, 0].row != first_cell.row and last_steps[step, 0].col != first_cell.col:
                # diagonal step
                distance += 1.42
            else:
                # straight step
                distance += 1.0
            first_cell = last_steps[step, 0]
        if time > 0:
            return distance * cell_scale / (time / 1000)
        else:
            return 0

    def __str__(self):
        return f"Pedestrians {self.id} standing on {self.cell}"

    def __eq__(self, other_ped):
        return self.id == other_ped.id


class Grid:
    """
    Grid class represents a 2D array of cells.
    """

    #######################################################################################################
    # Initialization functions
    #######################################################################################################
    def __init__(self, rows: int, cols: int, cells: np.ndarray = None,
                 cell_scale: float = 1.0):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        :param cells: np array of objects of type Cell that constitute the entire grid
        :param cell_scale: Size of each cell in meters.
        """
        super().__init__()

        # -> This is a list of numpy arrays of all the past states of
        # the grid starting from the initial state
        # self.past_pedestrian_states = []
        self.past_states = []

        self.rows: int = rows
        self.cols: int = cols
        self.cell_scale: float = cell_scale
        self.time_step: int = 0

        # Attributes used for visualization and animation
        # Standard colormap to homogenize all visualizations
        self.cmap = colors.ListedColormap(['blue', 'red', 'yellow', 'green'])
        self.animation = None
        # Construct an empty grid if the cells are not provided.
        if cells is None:
            self.cells = np.asarray([[Cell(row, column) for column in range(cols)] for row in range(rows)])
        else:
            self.cells = cells

        # Fill the cells with their attributes straight_neighbours and diagonal_neighbours based on the grid state.
        self.assign_neighbours()

        self.pedestrians = [Pedestrian(cell) for row in self.cells
                            for cell in row if cell.cell_type.value == 1]
        self.initial_state = self.cells.copy()

        # Store the points where measurements for pedestrian speed and density should be taken.
        # This can be filled by calling Grid.add_measuring_point
        self.measuring_points = []

    def set_cell_scale(self, cell_scale: float = 1):
        """
        Setter to set the attribute of cell size in meters
        :param cell_scale: size of a single cell in meters
        :return:
        """
        self.cell_scale = cell_scale

    def assign_neighbours(self):
        """
        This function assign a list to each cell. The list contains coordinates of cell's neighbors
        We divide neighbors into two parts. One part we name it straight_neighbors, 
        which include horizontal and vertical neighbors. Another includes diagonal neighbors.
        This is done in order to cater to speed of pedestrians.

        """
        for row in range(self.rows):
            for col in range(self.cols):
                column_list = [col - 1, col, col + 1]
                row_list = [row - 1, row, row + 1]
                for i in row_list:
                    for j in column_list:
                        if (0 <= i <= self.rows - 1) and (0 <= j <= self.cols - 1):
                            if (i - row) * (j - col) == 0:
                                self.cells[row][col].straight_neighbours.append(self.cells[i, j])
                            else:
                                self.cells[row][col].diagonal_neighbours.append(self.cells[i, j])
                self.cells[row][col].straight_neighbours.remove(self.cells[row, col])

    def change_cell_type(self, row: int, col: int) -> None:
        """
        Updates the type of the cell in the give indices and
        update the pedestrians list if necessary.

        This is used by the GUI when the user is selecting the cells and creating a custom scenario.
        :param row: row index
        :param col: column index
        :return: None
        """
        old_cell_type: np.short = np.short(self.cells[row, col].cell_type.value)
        new_cell_type: np.short = np.short((old_cell_type + 1) % 4)

        self.cells[row, col].cell_type = CellType(new_cell_type)
        # Update the pedestrians list
        if old_cell_type == 1 or new_cell_type == 1:
            self.pedestrians = [Pedestrian(cell) for row in self.cells
                                for cell in row if cell.cell_type.value == 1]

        if old_cell_type > 1 or new_cell_type > 1:
            self.cells[row, col].distance_to_target = np.inf \
                if new_cell_type == CellType.OBSTACLE.value else 0
            self.cells[row, col].dijkstra_cost = 0 \
                if new_cell_type == CellType.TARGET.value else np.inf

    def flood_pedestrians(self, density: float, distributed_speed: bool = False):
        """
        Floods the grid with pedestrians randomly based on a given density.
        Normally they will all have the same speed but otherwise they will have a speed extracted from the age vs speed
        graph defined in RiMEA figure 2
        :param density: pedestrians / meter. Please note that this is pedestrians per meter and not per cell!
        :param distributed_speed: Boolean if false all pedestrians have the same constant speed otherwise the speed is
                drawn from the age speed plot.
        :return: None
        """
        if density is None:
            print("Please supply a density.")
        else:
            grid_area = self.rows * self.cols * self.cell_scale ** 2
            no_of_pedestrians = int(density * grid_area)
            print("Adding", no_of_pedestrians, "to the grid.")
            seed(np.random.randint(0, 10))
            if distributed_speed:
                for ped in range(no_of_pedestrians):
                    # Draw the age of the pedestrian from a uniform distribution and calculate the corresponding speed
                    # from the age vs speed interpolation which is implemented in age_speed_distribution method,
                    ped_age = np.random.randint(18, 80)
                    rand_row = np.random.randint(0, self.rows)
                    rand_col = np.random.randint(0, self.cols)
                    while self.cells[rand_row, rand_col].cell_type.value != CellType.EMPTY.value:
                        rand_row = np.random.randint(0, self.rows)
                        rand_col = np.random.randint(0, self.cols)
                    self.add_pedestrian(rand_row, rand_col, speed=self.__age_speed_distribution(ped_age), age=ped_age)
            else:
                # We multiply the scaling factor to get the area in meters
                for ped in range(no_of_pedestrians):
                    rand_row = np.random.randint(0, self.rows)
                    rand_col = np.random.randint(0, self.cols)
                    while self.cells[rand_row, rand_col].cell_type.value != CellType.EMPTY.value:
                        rand_row = np.random.randint(0, self.rows)
                        rand_col = np.random.randint(0, self.cols)
                    self.add_pedestrian(rand_row, rand_col, speed=1.33)

    def __age_speed_distribution(self, age: int) -> float:
        """
        Using cubic spline, we formed an interpolator function that takes the age as the input and returns the pedestrian
        speed.
        :param age: Age of the pedestrian
        :return: Speed of the pedestrian
        """
        if age is None:
            print("Error")
        else:
            input_x = np.arange(5, 85, 5)
            y = [0.75, 1.23, 1.48, 1.65, 1.60, 1.55, 1.51, 1.49, 1.45, 1.42, 1.34, 1.25, 1.17, 1.05, 0.93, 0.67]
            output_y = np.array(y)
            coeff = spi.splrep(input_x, output_y, k=3)
            speed = spi.splev(age, coeff)
            return speed

    #######################################################################################################
    # Flood cost values functions
    #######################################################################################################
    def fill_distances(self, obstacle_avoidance: bool = True):
        """
        This method fills the cells with the cost which is simply the closest distance to the target
        :param obstacle_avoidance: Obstacle avoidance can be turned off with a simple bool. Normally it is on.
        :return: None
        """
        targets = [cell for row in self.cells
                   for cell in row if cell.cell_type.value == 3]
        for row in self.cells:
            for cell in row:
                min_dist = np.inf
                for target in targets:
                    distance = cell.get_distance(target, obstacle_avoidance)
                    if distance < min_dist:
                        cell.distance_to_target = distance
                        min_dist = distance

    def flood_dijkstra(self):
        """
        This function uses dijkstra's algorithm to floor all the cells that are part of the grid with a
        cost value as defined by the dijkstra's algorithm.

        We need to run the dijkstra's algorithm for each target since we would like to cater to multiple
        targets as well. Unlike the normal algorithm, in this case we take the target as the source (since we
        wish the distance at the target to be zero) and the pedestrian as the destination.
        :return: None
        """
        unvisited_cells = [cell for cell in self.cells.flatten() if
                           cell.cell_type.value is not CellType.OBSTACLE.value]
        # Once this list is empty the algorithm is complete
        while unvisited_cells:  # While the unvisited_cells is not empty
            cell_to_visit = min(unvisited_cells, key=lambda x: x.dijkstra_cost)
            for straight_neighbour in cell_to_visit.straight_neighbours:
                if straight_neighbour.cell_type.value != CellType.OBSTACLE.value \
                        and straight_neighbour in unvisited_cells:
                    dist = cell_to_visit.dijkstra_cost + cell_to_visit.get_distance(straight_neighbour)
                    if dist < straight_neighbour.dijkstra_cost:
                        straight_neighbour.dijkstra_cost = dist
            for diagonal_neighbour in cell_to_visit.diagonal_neighbours:
                if diagonal_neighbour.cell_type.value != CellType.OBSTACLE.value \
                        and diagonal_neighbour in unvisited_cells:
                    dist = cell_to_visit.dijkstra_cost + cell_to_visit.get_distance(diagonal_neighbour)
                    if dist < diagonal_neighbour.dijkstra_cost:
                        diagonal_neighbour.dijkstra_cost = dist
            unvisited_cells.remove(cell_to_visit)

    #######################################################################################################
    # Simulation functions
    #######################################################################################################
    def __pedestrians_costs(self, p1: Pedestrian, neighbor: Cell) -> float:
        """
        calculate the sum of costs due to all other pedestrians on the specific  cell
        :param p1: the pedestrian for which the neighbouring cell pedestrian cost is being calculated
        :param neighbor: the neighbouring cell in question
        :return: cost of the neighbouring cell due to pedestrians. Note the intrinsic cost is separate
        """
        costs = 0
        for p2 in self.pedestrians:
            if p2 != p1:
                costs += neighbor.cost_to_pedestrian(p2)
        return costs

    def __get_cell_cost(self, dijkstra, ped, cell):
        """
        get the total cost associated to the cell
        :param dijkstra: If true calculates the cost from the dijkstra's algorithm otherwise the normal distance
        to target is considered.
        :param ped: the pedestrian which has to move
        :param cell: the cell in question
        :return: total cost of the cell.
        """
        pc = self.__pedestrians_costs(ped, cell)
        if dijkstra:
            return cell.dijkstra_cost + pc
        else:
            return cell.distance_to_target + pc

    def __choose_best_neighbor(self, dijkstra: bool, ped: Pedestrian):
        """
        Based on the minimum cost selects the best candidate cell for the next move.
        :param dijkstra: If true calculates the cost from the dijkstra's algorithm otherwise the normal distance
        to target is considered.
        :param ped: the pedestrian which has to move
        :return: the cell which is the best choice for the next move.
        """
        selected_cell = ped.cell
        min_distance = self.__get_cell_cost(dijkstra, ped, selected_cell)
        for nc in ped.cell.straight_neighbours:
            # if nc.cell_type.value == 1 or nc.cell_type.value == 2:
            #     continue
            if nc.cell_type.value == 3:
                return nc
            else:
                cell_cost = self.__get_cell_cost(dijkstra, ped, nc)
                if cell_cost < min_distance:
                    selected_cell = nc
                    min_distance = cell_cost
        for nc in ped.cell.diagonal_neighbours:
            # if nc.cell_type.value == 1 or nc.cell_type.value == 2:
            #     continue
            if nc.cell_type.value == 3:
                return nc
            else:
                cell_cost = self.__get_cell_cost(dijkstra, ped, nc)
                if cell_cost < min_distance:
                    selected_cell = nc
                    min_distance = cell_cost
        return selected_cell

    def update_grid(self, current_time: int = 0, max_steps: int = 100,
                    dijkstra: bool = False, absorbing_targets: bool = True, 
                    constant_speed: bool = True, periodic_boundary: bool = False):
        """
        this method updates moves the pedestrians who didn't reach the target yet.
        Pedestrians move horizontally & vertically one step per time step
        While they move 0.7 of a step diagonally
        Details on how that is calculated can be found in Pedestrian.move

        dijkstra: whether to sue the dijkstra algorithm for cost calculations or not
        absorbing_targets: decides if the pedestrians disappear once they reach the target
        :param periodic_boundary: flag to identify if the right boundary is periodic. Currently only works with
                                    RiMEA 4 case
        :param current_time: The current clock time
        :param max_steps: the maximum number of updates that need to be made.
        :param dijkstra: Boolean flag indicates if the cost to be calculated is driven from the dijkstra's algorithm or not
        :param absorbing_targets: Flag deciding if the pedestrians should disappear once they reach a target.
        :param constant_speed: defines if the pedestrians maintain a constant speed.
        :param periodic_boundary: Flag that defines if the pedestrians move in a carousel.
        :return: None
        """
        # save the current state of the grid
        if constant_speed:
            self.past_states.append(self.to_array())
            self.time_step += 1
        # pedestrians who reached the target
        to_remove_peds = []
        for ped in self.pedestrians:
            # teleport pedestrian to start if the periodic boundary condition is set to true.
            if periodic_boundary:
                if ped.cell.check_if_neighbour_is_target():
                    next_row = ped.cell.row
                    next_col = 0
                    # Teleport the pedestrian to the start if the periodic BC are activated.
                    # This only works for RiMEA 4 currently
                    if self.cells[next_row, next_col].cell_type.value == CellType.EMPTY.value:
                        ped.update_cell(self.cells[next_row, next_col])
                        self.document_measures(self.cells[next_row, next_col],
                                               current_time, ped)
                        continue
                    # If the first cell is not free then make the pedestrian wait.
                    else:
                        continue

            selected_cell = self.__choose_best_neighbor(dijkstra, ped)
            # Get the distance the pedestrian should move
            ped_row, ped_col, diag_bool = ped.move(selected_cell, current_time=current_time,
                                                   constant_speed=constant_speed,
                                                   max_steps=max_steps, cell_scale=self.cell_scale)

            # check if a complete diagonal step is possible.
            if np.abs(ped_row) >= 1.0 and np.abs(ped_col) >= 1.0:
                # Check if the pedestrian should move a diagonally
                ped.update_cell(selected_cell)
                if selected_cell in self.measuring_points:
                    self.document_measures(selected_cell, current_time, ped)
            if not diag_bool:
                # Check if the pedestrian should move horizontally/vertically
                if np.abs(ped_row) >= 1.0 or np.abs(ped_col) >= 1.0:
                    ped.update_cell(selected_cell)
                    if selected_cell in self.measuring_points:
                        self.document_measures(selected_cell, current_time, ped)

            # If a target is reached remove the pedestrian provided the targets are absorbing,
            # otherwise update the new cell
            if absorbing_targets:
                if ped.cell.cell_type.value != CellType.TARGET.value:
                    ped.cell.cell_type = CellType.PEDESTRIAN
                else:
                    to_remove_peds.append(ped)
            else:
                if ped.cell.cell_type.value != CellType.TARGET.value:
                    ped.cell.cell_type = CellType.PEDESTRIAN

        # Remove pedestrians who reached the target
        self.pedestrians = [ped for ped in self.pedestrians if ped not in to_remove_peds]

    def simulate(self, no_of_steps, dijkstra=False, absorbing_targets=True, step_time: int = 300,
                 obstacle_avoidance: bool = True):
        """
        This method executes the simulation based on the type of cost function (rudimentary or dijkstra assigned)
        and stores all the states of the grid in an attribute

        :param obstacle_avoidance: boolean flag that determines if the pedestrians should avoid obstacles.
                                This is just for demonstration purposes
        :param step_time: how long of a delay exists between steps.
        :param absorbing_targets: boolean flag that decides if the pedestrians disappear when they reach a target.
        :param no_of_steps: How many steps to simulate
        :param dijkstra: whether the cost should be based on the dijkstra's algorithm
        :return: List of past states of the scenario
        """
        self.past_states = []
        self.cells = self.initial_state
        if dijkstra:
            self.flood_dijkstra()
        else:
            self.fill_distances(obstacle_avoidance=obstacle_avoidance)
        while self.pedestrians and self.time_step <= no_of_steps:
            self.update_grid(dijkstra=dijkstra, absorbing_targets=absorbing_targets)
        print("The simulation was took", self.time_step, "steps and was executed in", self.time_step * step_time / 1000,
              "seconds.")
        return self.past_states

    #######################################################################################################
    # Visiulization functions
    #######################################################################################################
    def document_measures(self, measuring_point, current_time, ped):
        """
        Stores various parameters for the pedestrians who step into the measurement cells in a csv file in the logs folder.
        :param measuring_point: The current measuring point cell
        :param current_time: Time since the start of the simulation in milliseconds
        :param ped: the pedestrian passing through the measuring point
        :return:
        """
        density = self.measure_density(measuring_point)
        speed = ped.measure_speed(cell_scale=self.cell_scale)
        if Path("./logs/measuring_points_logs.csv").exists():
            # Append to file
            measuring_points_logs = open("./logs/measuring_points_logs.csv", "a", newline="")
            measuring_points_row = [ped.id, ped.age, measuring_point.row, measuring_point.col, current_time, density,
                                    speed]
            writer = csv.writer(measuring_points_logs)
            writer.writerow(measuring_points_row)
        else:
            # If file doesnt exist then create it.
            measuring_points_logs = open("./logs/measuring_points_logs.csv", "a", newline="")
            headers = ["Pedestrian_id", "Pedestrian_Age", "measuring_row", "measuring_col", "time", "density", "speed"]
            writer = csv.writer(measuring_points_logs)
            writer.writerow(headers)
            measuring_points_row = [ped.id, ped.age, measuring_point.row, measuring_point.col, current_time, density,
                                    speed]
            writer.writerow(measuring_points_row)
        measuring_points_logs.close()

    def measure_density(self, measuring_point):
        """
        Grid class function that records the density of pedestrians in a certain region.
        :param measuring_point: The current measuring point cell
        :return:
        """

        # Find the 10x10 square around (row,col)
        # The 10 rows are [row - 4, row + 5]
        # However, if row < 4 for example 3
        # then the rows are [0, 9]
        # and if row = 17 out of 20 rows overall in the grid
        # Then rows are [10, 19]
        # Similarly for columns

        row_min = measuring_point.row - 4 if measuring_point.row >= 4 else 0
        row_max = measuring_point.row + 5 if measuring_point.row + 5 < self.rows else self.rows - 1
        if row_max - measuring_point.row < 5:
            row_min = row_min - (5 - (row_max - measuring_point.row)) \
                if row_min - (5 - (row_max - measuring_point.row)) >= 0 else 0
        if measuring_point.row < 4:
            # row_min == 0
            row_max = 9 if 9 < self.rows else self.rows - 1

        col_min = measuring_point.col - 4 if measuring_point.col >= 4 else 0
        col_max = measuring_point.col + 5 if measuring_point.col + 5 < self.cols else self.cols - 1
        if col_max - measuring_point.col < 5:
            col_min = col_min - (5 - (col_max - measuring_point.col)) \
                if col_min - (5 - (col_max - measuring_point.col)) >= 0 else 0
        if measuring_point.col < 4:
            # col_min == 0
            col_max = 9 if 9 < self.cols else self.cols - 1

        # Count pedestrians in the square
        pedestrians_count = len([1 for r in range(row_min, row_max)
                                 for c in range(col_min, col_max) if self.cells[r, c].cell_type.value == 1])
        # Scale the area according to cell_scale
        measuring_area = ((row_max - row_min) * (col_max - col_min)) * (self.cell_scale * self.cell_scale)

        return pedestrians_count / measuring_area

    def add_pedestrian(self, row: int, col: int, speed: float = 1.33,
                       age: int = 20) -> None:
        """
        Creates a new pedestrian on this grid and set the cell type where the pedestrian exists to pedestrian type.
        :param row: The row of the cell where the pedestrian is initially standing
        :param col: The column of the cell where the pedestrian is initially standing
        :param speed: (Optional) The average speed of the pedestrian in meter/second
        :param age: The age of the pedestrian
        :return: None
        """
        self.pedestrians.append(Pedestrian(self.cells[row, col], speed=speed, age=age))
        self.cells[row, col].cell_type = CellType.PEDESTRIAN

    def add_measuring_point(self, row: int, col: int) -> None:
        """
        Creates a measuring point on this grid. The density and speeds are recorded at these points and stored in a log file.
        :param row: The row of the cell where the pedestrian is initially standing
        :param col: The column of the cell where the pedestrian is initially standing
        :return: None
        """
        self.measuring_points.append(self.cells[row, col])

    def to_array(self) -> np.ndarray:
        """
        This function reads the grid object and converts it into a numpy array with following encoding
        Array encoding rule
            0: Empty Cell
            1. Pedestrian Cell
            2. Obstacle Cell
            3. Target Cell
        All array entries will be ints or floats

        For more details on the class structure please see the report or the Class docstring.

        :return: numpy array
        """
        array = np.asarray([[cell.cell_type.value for cell in row] for row in self.cells])
        return array

    def animation_frame(self, i):
        """
        This method is a helper method called by the FuncAnimation function to update the animation
        :param i: frame number
        :return: updated image
        """
        self.animation.set_array(self.past_states[i])
        return self.animation

    def animate(self):
        """
        This method creates an animation of the simulation.
        Note in order ot create an animation, past states need to exist.
        :return: anim: Animation object
        """
        assert len(self.past_states) != 0
        cmap = self.cmap
        bounds = [0, 1, 2, 3, 4]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        fig, ax = plt.subplots(figsize=(10, 10))
        self.animation = ax.imshow(self.past_states[0], cmap=cmap, norm=norm)
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
        ax.set_xticks(np.arange(-.5, self.cols, 1))
        ax.set_yticks(np.arange(-.5, self.rows, 1))
        # draw gridlines
        anim = animation.FuncAnimation(
            fig,
            self.animation_frame,
            frames=len(self.past_states),  # nSeconds * fps,
            interval=10000 / 30  # 10000 / fps,  # in ms
        )
        plt.show()
        return anim

    #######################################################################################################
    # Debugging functions
    #######################################################################################################
    def get_dijkstra(self) -> np.ndarray:
        """
        :return: Returns the numpy array that contain all the dijkstra costs for each cell.
        """
        dijkstra_array = []
        for row in self.cells:
            d_row = []
            for cell in row:
                d_row.append(cell.dijkstra_cost)
            dijkstra_array.append(d_row)
        dijkstra_array = np.asarray(dijkstra_array)
        return dijkstra_array

    def get_distance_to_target(self) -> np.ndarray:
        """
        :return: Returns the numpy array that contain all the dijkstra costs for each cell.
        """
        dist_to_target = []
        for row in self.cells:
            d_row = []
            for cell in row:
                d_row.append(cell.distance_to_target)
            dist_to_target.append(d_row)
        dist_to_target = np.asarray(dist_to_target)
        return dist_to_target

    def is_valid(self):
        """
        Checks if all cells in the grid are valid cells and that there are no illegal overlap
        :return: true or false with an error message
        """
        if any(not ped.is_valid() for ped in self.pedestrians):
            return False, "Some pedestrians are standing on cells with invalid types"

        for i in range(len(self.pedestrians)):
            for j in range(i + 1, len(self.pedestrians)):
                if self.pedestrians[i].cell.row == self.pedestrians[j].cell.row and \
                        self.pedestrians[i].cell.col == self.pedestrians[j].cell.col:
                    return False, f"pedestrians {self.pedestrians[i].id} and {self.pedestrians[j].id} " \
                                  f"are standing on the same cell"
        return True, "The grid is valid"

    def __str__(self):
        res = ""
        for row in self.cells:
            for cell in row:
                res += f"{cell.cell_type.value} "
            res += "\n"
        return res
