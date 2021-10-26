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
        """
        super().__init__()
        self.row: np.int = row
        self.col: np.int = col
        self.cell_type: CellType = cell_type
        if obstacle_avoidance:
            self.distance_to_target: np.float = np.inf if self.cell_type.value == CellType.OBSTACLE.value else 0
        else:
            self.distance_to_target = 0
        # self.cost: np.float = np.inf if self.cell_type.value == CellType.OBSTACLE.value else 0
        self.straight_neighbours = []
        self.diagonal_neighbours = []
        self.dijkstra_cost = 0 if self.cell_type.value == CellType.TARGET.value else np.inf
        self.path: bool = False  # did a pedestrian pass through this cell, for visualization only

    def get_distance(self, other_cell, obstacle_avoidance: bool=True) -> np.float:
        """
        get distance to another cell if the cell is not of type obstacle.
        :param other_cell: cell from which distance has to be calculated
        obstacle_avoidance: if false ignores all obstacles
        :return: euclidean distance as a np.float
        """

        if obstacle_avoidance:
            if self.cell_type.value == 2:
                return np.inf
            else:
                return np.sqrt(np.power(self.row - other_cell.row, 2) + np.power(self.col - other_cell.col, 2))
        else:
            return np.sqrt(np.power(self.row - other_cell.row, 2) + np.power(self.col - other_cell.col, 2))

    def cost_to_pedestrian(self, ped, r_max: np.float = 1.5) -> np.float:
        """
        get cost added by a pedestrian to this cell
        :param ped: A pedestrian to whom to calculate the distance cost
        :param r_max:
        :return: the cost calculated based on the distance to the pedestrian
        """
        r: np.float = self.get_distance(ped.cell)

        if r >= r_max:
            return 0
        else:
            # return np.exp(1 / (r * r - r_max * r_max))
            return 1/np.exp(r * r - r_max * r_max)


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
        :return: a pair of float indicating the distance & direction the pedestrian should move
        """
        if self.cell.row != cell.row and self.cell.col != cell.col:
            # diagonal step
            # the pedestrian only moves 0.7 horizontally & vertically
            self.row = self.row + (cell.row - self.cell.row) * 0.71
            self.col = self.col + (cell.col - self.cell.col) * 0.71
            full_row = self.row
            full_col = self.col
            # remove the potential 1 from self.row & self.col keeping the sign
            self.row = (self.row % 1.0) * np.sign(self.row)
            self.col = (self.col % 1.0) * np.sign(self.col)
            return full_row, full_col
        else:
            # straight step
            return (cell.row - self.cell.row), (cell.col - self.cell.col)

    def __str__(self):
        return f"Pedestrians {self.id} standing on {self.cell}"

    def __eq__(self, other_ped):
        return self.id == other_ped.id


class Grid:
    """
    Grid class represents a 2D array of cells.
    """

    def __init__(self, rows: int, cols: int, cells: np.ndarray = None, obstacle_avoidance: bool = True):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        :param obstacle_avoidance: if false, obstacles are ignored
        """
        super().__init__()

        # -> This is a list of numpy arrays of all the past states of
        # the grid starting from the initial state
        self.past_pedestrian_states = []
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
        self.get_current_state()
        self.initial_state = self.cells.copy()
        self.fill_distances(obstacle_avoidance=obstacle_avoidance)  # Fills the cells with the cost as a parameter
                                                                    # to the distance to the target
        self.flood_dijkstra()  # Fills the cells with the cost as per the dijkstra's algorithm

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

    def __find_pedestrian(self, row: int, col: int) -> Pedestrian:
        for ind, ped in enumerate(self.pedestrians):
            if ped.cell.row == row and \
                    ped.cell.col == col:
                return ped

    def change_cell_type(self, row: int, col: int) -> None:
        """
        Updates the type of the cell in the give indices and
        update the pedestrians list if necessary
        :param row: row index
        :param col: column index
        :return: None
        """
        old_cell_type = self.cells[row, col].cell_type
        new_cell_type = (old_cell_type.value + 1) % 4

        if old_cell_type.value == 1:
            self.pedestrians = [ped for ped in self.pedestrians if not ped.cell.row == row or not ped.cell.col == col]
        elif new_cell_type == 1:
            self.pedestrians.append(Pedestrian(self.cells[row, col]))
            self.cells[row, col].dijkstra_cost = np.inf
        elif new_cell_type == 3:
            # If cell if target then the dijkstra cost should be zero
            self.cells[row, col].dijkstra_cost = 0
        elif new_cell_type == 2:
            # If cell if target then the obstical cost for rudementary avoidance should be infinity.
            self.cells[row, col].distance_to_target = np.inf
            self.cells[row, col].dijkstra_cost = np.inf
        else:
            self.cells[row, col].dijkstra_cost = np.inf

        self.cells[row, col].cell_type = CellType(new_cell_type)

        if old_cell_type.value == 3 or new_cell_type == 3:
            self.fill_distances()
            self.flood_dijkstra()

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

    def __str__(self):
        res = ""
        for row_ind, row in enumerate(self.cells):
            for col_ind, cell in enumerate(row):
                res += f"{cell.cell_type.value} "
            res += "\n"
        return res

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

    def get_current_state(self):
        """
        This function can read the coordinates of all pedestrians at current step
        and store it in self.past_states for plotting later.
        :param: grid -> Grid class
        """
        current_state = []
        for pedestrian in self.pedestrians:
            current_state.append([pedestrian.cell.row, pedestrian.cell.col])
        self.past_pedestrian_states.append(current_state)

    def fill_distances(self, obstacle_avoidance: bool = True):
        """
        This method fills the cells with the cost which is simply the closest distance to the target
        :param obstacle_avoidance: Obstacle avoidance can be turned off with a simple bool. Normally it is on.
        :return: None
        """
        targets = [cell for row in self.cells
                   for cell in row if cell.cell_type.value == 3]
        for row_ind, row in enumerate(self.cells):
            for col_ind, cell in enumerate(row):
                min_dist = np.inf
                for tar_ind, target in enumerate(targets):
                    distance = cell.get_distance(target, obstacle_avoidance)
                    if cell.get_distance(target, obstacle_avoidance) < min_dist:
                        cell.distance_to_target = distance
                        min_dist = distance

    def __pedestrians_costs(self, p1: Pedestrian, neighbor: Cell) -> np.float:
        """
        calculate the sum of all other pedestrians on the neighbor cell
        :param p1:
        :param neighbor:
        :return:
        """
        costs = 0
        for ind, p2 in enumerate(self.pedestrians):
            if p2.id != p1.id:
                costs += neighbor.cost_to_pedestrian(p2)
        return costs

    def __get_cell_cost(self, dijkstra, ped, cell):
        pc = self.__pedestrians_costs(ped, cell)
        # print("pedestrian", pc)
        if dijkstra:
            return cell.dijkstra_cost + pc
        else:
            return cell.distance_to_target + pc

    def __choose_best_neighbor(self, dijkstra, ped):
        selected_cell = ped.cell
        min_distance = self.__get_cell_cost(dijkstra, ped, selected_cell)
        # print("START", min_distance)
        # if dijkstra:
        #     min_distance = selected_cell.dijkstra_cost
        # else:
        #     min_distance = selected_cell.distance_to_target
        # TODO consider cost to pedestrians or other parameters
        # TODO maybe this function be updated to have the kind of distance as a parameter
        for nc_ind, nc in enumerate(ped.cell.straight_neighbours):
            cell_cost = self.__get_cell_cost(dijkstra, ped, nc)
            if cell_cost < min_distance:
                selected_cell = nc
                min_distance = cell_cost
        for nc_ind, nc in enumerate(ped.cell.diagonal_neighbours):
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
        for ped_ind, ped in enumerate(self.pedestrians):
            selected_cell = self.__choose_best_neighbor(dijkstra, ped)
            # Get the distance the pedestrian should move
            ped_row, ped_col = ped.move(selected_cell)

            # Check if the pedestrian should move a full cell vertically
            if np.abs(ped_row) >= 1.0:
                ped.cell.cell_type = CellType.EMPTY
                ped.cell.path = True
                ped.cell = self.cells[ped.cell.row + (selected_cell.row - ped.cell.row), ped.cell.col]

            # Check if the pedestrian should move a full cell horizontally
            if np.abs(ped_col) >= 1.0:
                if np.abs(ped_row) < 1.0:
                    ped.cell.cell_type = CellType.EMPTY
                    ped.cell.path = True
                ped.cell = self.cells[ped.cell.row, ped.cell.col + (selected_cell.col - ped.cell.col)]

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

    def simulate(self, no_of_steps, dijkstra=False, absorbing_targets = True):
        """
        This method executes the simulation based on the type of cost function (rudementary or dijkstra assigned)
        and stores all the states of the grid in an attribute

        :param no_of_steps: How many steps to simulate
        :param dijkstra: whether the cost should be based on the dijkstra's algorithm
        :return: List of past states of the scenario
        """
        self.past_states = []
        self.cells = self.initial_state
        for step in range(no_of_steps):
            self.update_grid(dijkstra=dijkstra, absorbing_targets=absorbing_targets)
            if not self.pedestrians:
                break
        print("The simulation was took", self.time_step, "steps.")
        return self.past_states

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
                    if straight_neighbour.cell_type.value != CellType.OBSTACLE.value:
                        dist = cell_to_visit.dijkstra_cost + cell_to_visit.get_distance(straight_neighbour)
                        if dist < straight_neighbour.dijkstra_cost:
                            straight_neighbour.dijkstra_cost = dist
                for diagonal_neighbour in cell_to_visit.diagonal_neighbours:
                    if diagonal_neighbour.cell_type.value != CellType.OBSTACLE.value:
                        dist = cell_to_visit.dijkstra_cost + cell_to_visit.get_distance(diagonal_neighbour)
                        if dist < diagonal_neighbour.dijkstra_cost:
                            diagonal_neighbour.dijkstra_cost = dist
                unvisited_cells.remove(cell_to_visit)

    def get_dijkstra(self) -> np.ndarray:
        """
        :return: Returns the numpy array that contain all the dijkstra costs for each cell.
        """
        dijkstra_array = []
        for row_ind, row in enumerate(self.cells):
            d_row = []
            for col_ind, cell in enumerate(row):
                d_row.append(cell.dijkstra_cost)
            dijkstra_array.append(d_row)
        dijkstra_array = np.array(dijkstra_array)
        return dijkstra_array

    def get_distance_to_target(self):
        """
        :return: Returns the numpy array that contain all the dijkstra costs for each cell.
        """
        dist_to_target = []
        for row_ind, row in enumerate(self.cells):
            d_row = []
            for col_ind, cell in enumerate(row):
                d_row.append(cell.distance_to_target)
            dist_to_target.append(d_row)
        dist_to_target = np.array(dist_to_target)
        return dist_to_target

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
