from enum import Enum

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors



class CellType(Enum):
    EMPTY = 0
    PEDESTRIAN = 1
    OBSTACLE = 2
    TARGET = 3


class Cell:
    """
    Cell class represents one cell in the grid. A cell can be a target, an obstacle or empty
    """

    def __init__(self, row: int, col: int, cell_type: CellType = CellType.EMPTY, obstacle_avoidance: bool = True):
        """
        Initiate the cell with the given position to an empty cell
        :param row: represents the cell position in the y-axis
        :param col: represents the cell position in the x-axis
        :param cell_type: the type of the cell
        :param obstacle_avoidance: if false, obstacles are ignored

        """
        super().__init__()
        self.row: np.int = row
        self.col: np.int = col
        self.cell_type: CellType = cell_type
        if obstacle_avoidance:
            self.distance_to_target: np.float = np.inf if self.cell_type.value == CellType.OBSTACLE.value else 0
        else:
            self.distance_to_target = 0
        self.straight_neighbours = []
        self.diagonal_neighbours = []
        self.dijkstra_cost = 0 if self.cell_type.value == CellType.TARGET.value else np.inf
        self.path: bool = False  # did a pedestrian pass through this cell, for visualization only

    def get_distance(self, other_cell, obstacle_avoidance: bool = True) -> np.float:
        """
        get distance to another cell if the cell is not of type obstacle.
        :param other_cell: cell from which distance has to be calculated
        :param obstacle_avoidance: if false ignores all obstacles
        :return: euclidean distance as a np.float
        """

        if obstacle_avoidance:
            if self.cell_type.value == CellType.OBSTACLE.value:
                return np.inf
            else:
                return np.sqrt(np.power(self.row - other_cell.row, 2) + np.power(self.col - other_cell.col, 2))
        else:
            return np.sqrt(np.power(self.row - other_cell.row, 2) + np.power(self.col - other_cell.col, 2))

    def cost_to_pedestrian(self, ped, r_max: np.float = 1.2) -> np.float:
        """
        get cost added by a pedestrian to this cell
        :param ped: A pedestrian to whom to calculate the distance cost
        :param r_max: Maximum distance to start avoiding other pedestrians
        :return: the cost calculated based on the distance to the pedestrian
        """
        r: np.float = self.get_distance(ped.cell)
        if r >= r_max:
            return 0
        else:
            # return np.exp(1 / (r * r - r_max * r_max))
            return 1 / np.exp(r * r - r_max * r_max)

    def __str__(self):
        return f"Cell ({self.row}, {self.col}) Type = {self.cell_type}"

    def __eq__(self, other_cell):
        return self.row == other_cell.row and self.col == other_cell.col

    def __ge__(self, other_cell):
        return self.distance_to_target + self.cost >= \
               other_cell.distance_to_target + other_cell.cost


class Pedestrian:
    """
    A Pedestrian has a unique cell and a unique id.
    The cell is updated after every step based on a utility function.
    """
    _id_counter: np.int = 0

    def __init__(self, cell: Cell):
        """
        Initiate the pedestrian with the given position & a unique id.
        :param cell: represents the cell where the pedestrian is standing
        row & col in a pedestrian serve to store partial step
        this helps creating more accurate diagonal speed
        """
        super().__init__()
        Pedestrian._id_counter += 1
        self.id: np.int = Pedestrian._id_counter
        self.cell: Cell = cell
        self.row: np.float = 0
        self.col: np.float = 0

    def is_valid(self) -> bool:
        """
        Checks that the cell where the pedestrian is standing is a pedestrian cell.
        :return: true or false
        """
        return self.cell.cell_type.value == CellType.PEDESTRIAN.value

    def move(self, cell: Cell) -> (np.float, np.float):
        """
        Changes the cell the pedestrian is standing on.
        :param cell: The cell where the pedestrian needs to move
        :return: a pair of float indicating the distance & direction the pedestrian should move and a bool stating is the move is diagonal or not
        """
        if self.cell.row != cell.row and self.cell.col != cell.col:
            # diagonal step
            # the pedestrian only moves 0.7 horizontally & vertically
            full_row = self.row + (cell.row - self.cell.row) * 0.71
            full_col = self.col + (cell.col - self.cell.col) * 0.71
            # remove the potential 1 from self.row & self.col keeping the sign if a diagonal step can be made
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
    def __init__(self, rows: int, cols: int, cells: np.ndarray = None):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        """
        super().__init__()

        # -> This is a list of numpy arrays of all the past states of
        # the grid starting from the initial state
        # self.past_pedestrian_states = []
        self.past_states = []

        self.rows: np.int = rows
        self.cols: np.int = cols
        self.time_step: np.int = 0

        # Attributes used for visualization and animation
        # Standard colormap to homogenize all visualizations
        self.cmap = colors.ListedColormap(['blue', 'red', 'yellow', 'green'])
        self.animation = None
        if cells is None:
            self.cells = np.array([[Cell(row, column) for column in range(cols)] for row in range(rows)])
        else:
            self.cells = cells
        self.assign_neighbours()

        self.pedestrians = [Pedestrian(cell) for row in self.cells
                            for cell in row if cell.cell_type.value == 1]
        # self.get_current_state()
        self.initial_state = self.cells.copy()

    def assign_neighbours(self):
        """
        This function assign a list to each cell. The list contains coordinates of cell's neighbors
        We divide neighbors into two parts. One part we name it straight_neighbors, 
        which include horizontal and vertical neighbors. Another includes diagonal neighbors.
        This is done in order to cater to speed of pedestrians.

        :param: grid -> Grid class
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
        update the pedestrians list if necessary
        :param row: row index
        :param col: column index
        :return: None
        """
        old_cell_type = self.cells[row, col].cell_type.value
        new_cell_type = (old_cell_type + 1) % 4

        self.cells[row, col].cell_type = CellType(new_cell_type)
        # Update the pedestrians list
        if old_cell_type == 1 or new_cell_type == 1:
            self.pedestrians = [Pedestrian(cell) for row in self.cells
                                for cell in row if cell.cell_type.value == 1]

        if old_cell_type > 1 or new_cell_type > 1:
            self.cells[row, col].distance_to_target = np.inf if new_cell_type == CellType.OBSTACLE.value else 0
            self.cells[row, col].dijkstra_cost = 0 if new_cell_type == CellType.TARGET.value else np.inf

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
                    if cell.get_distance(target, obstacle_avoidance) < min_dist:
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
        targets = [cell for row in self.cells
                   for cell in row if cell.cell_type.value == 3]

        for target in targets:
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
    def __pedestrians_costs(self, p1: Pedestrian, neighbor: Cell) -> np.float:
        """
        calculate the sum of all other pedestrians on the neighbor cell
        :param p1:
        :param neighbor:
        :return:
        """
        costs = 0
        for p2 in self.pedestrians:
            if p2 != p1:
                costs += neighbor.cost_to_pedestrian(p2)
        return costs

    def __get_cell_cost(self, dijkstra, ped, cell):
        pc = self.__pedestrians_costs(ped, cell)
        if dijkstra:
            return cell.dijkstra_cost + pc
        else:
            return cell.distance_to_target + pc

    def __choose_best_neighbor(self, dijkstra: bool, ped: Pedestrian):
        selected_cell = ped.cell
        min_distance = self.__get_cell_cost(dijkstra, ped, selected_cell)
        for nc in ped.cell.straight_neighbours:
            if nc.cell_type.value == 1 or nc.cell_type.value == 2:
                continue
            elif nc.cell_type.value == 3:
                return nc
            else:
                cell_cost = self.__get_cell_cost(dijkstra, ped, nc)
                if cell_cost < min_distance:
                    selected_cell = nc
                    min_distance = cell_cost
        for nc in ped.cell.diagonal_neighbours:
            if nc.cell_type.value == 1 or nc.cell_type.value == 2:
                continue
            elif nc.cell_type.value == 3:
                return nc
            else:
                cell_cost = self.__get_cell_cost(dijkstra, ped, nc)
                if cell_cost < min_distance:
                    selected_cell = nc
                    min_distance = cell_cost
        return selected_cell

    def update_grid(self, dijkstra=False, absorbing_targets=True):
        """
        this method updates moves the pedestrians who didn't reach the target yet.
        Pedestrians move horizontally & vertically one step per time step
        While they move 0.7 of a step diagonally
        Details on how that is calculated can be found in Pedestrian.move

        dijkstra: whether to sue the dijkstra algorithm for cost calculations or not
        absorbing_targets: decides if the pedestrians disappear once they reach the target
        :return: None
        """
        self.time_step += 1
        # save the current state of the grid
        self.past_states.append(self.to_array())
        # pedestrians who reached the target
        to_remove_peds = []
        for ped in self.pedestrians:
            selected_cell = self.__choose_best_neighbor(dijkstra, ped)
            # Get the distance the pedestrian should move
            ped_row, ped_col, diag_bool = ped.move(selected_cell)
            # if ped.id == 1:
            #     print(ped.cell.row, ped.cell.col, ped_row, ped_col, ped.id)
            if np.abs(ped_row) >= 1.0 and np.abs(ped_col) >= 1.0:
                # Check if the pedestrian should move a diagonally
                # if ped.id == 1:
                #     print(ped.cell.row, ped.cell.col, "MOVED")
                ped.cell.cell_type = CellType.EMPTY
                ped.cell.path = True
                ped.cell = self.cells[selected_cell.row, selected_cell.col]
            if not diag_bool:
                # Check if the pedestrian should move horizontally/virtically
                if np.abs(ped_row) >= 1.0 or np.abs(ped_col) >= 1.0:
                    ped.cell.cell_type = CellType.EMPTY
                    ped.cell.path = True
                    ped.cell = self.cells[selected_cell.row, selected_cell.col]

            # TODO: Remove comment
            # Check if the pedestrian should move a full cell horizontally
            # if np.abs(ped_col) >= 1.0:
            #     if np.abs(ped_row) < 1.0:
            #         ped.cell.cell_type = CellType.EMPTY
            #         ped.cell.path = True

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

    def simulate(self, no_of_steps, dijkstra=False, absorbing_targets=True, step_time = 300, obstacle_avoidance:bool=True):
        """
        This method executes the simulation based on the type of cost function (rudementary or dijkstra assigned)
        and stores all the states of the grid in an attribute

        :param no_of_steps: How many steps to simulate
        :param dijkstra: whether the cost should be based on the dijkstra's algorithm
        :return: List of past states of the scenario
        """
        total_time = 0
        self.past_states = []
        self.cells = self.initial_state
        if dijkstra:
            self.flood_dijkstra()
        else:
            self.fill_distances(obstacle_avoidance=obstacle_avoidance)
        while self.pedestrians and self.time_step <= no_of_steps:
            self.update_grid(dijkstra=dijkstra, absorbing_targets=absorbing_targets)
        print("The simulation was took", self.time_step, "steps and was executed in", self.time_step * step_time/1000, "seconds.")
        return self.past_states

    #######################################################################################################
    # Visiulization functions
    #######################################################################################################
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
        array = np.array([[cell.cell_type.value for cell in row] for row in self.cells])
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
        This method creates an animation of the simulation. Note in order ot create an animation, past states need to exist.
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
        dijkstra_array = np.array(dijkstra_array)
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
        dist_to_target = np.array(dist_to_target)
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
            for col_ind, cell in row:
                res += f"{cell.cell_type.value} "
            res += "\n"
        return res