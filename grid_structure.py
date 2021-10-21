from enum import Enum
import numpy as np


class CellType(Enum):
    EMPTY = 0
    PEDESTRIAN = 1
    OBSTACLE = 2
    TARGET = 3


class Cell:
    """
    Cell class represents one cell in the grid. A cell can be a target, an obstacle or empty
    """

    def __init__(self, row: int, col: int, cell_type: CellType = CellType.EMPTY):
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
        self.distance_to_target: np.float = 0
        self.cost: np.float = 0
        self.straight_neighbours: np.ndarray = np.array([])
        self.diagonal_neighbours: np.ndarray = np.array([])

    def cost_to_pedestrian(self, ped, r_max: np.float) -> np.float:
        """
        get cost added by a pedestrian to this cell
        :param ped: A pedestrian to whom to calculate the distance cost
        :param r_max:
        :return: the cost calculated based on the distance to the pedestrian
        """
        r: np.float = self.get_distance(ped.cell)
        if r < r_max:
            return 0
        else:
            return np.exp(1 / (r * r - r_max * r_max))

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
        """
        super().__init__()
        Pedestrian._id_counter += 1
        self.id: np.int = Pedestrian._id_counter
        self.cell: Cell = cell

    def is_valid(self) -> bool:
        """
        Checks that the cell where the pedestrian is standing is a pedestrian cell.
        :return: true or false
        """
        return self.cell.cell_type == CellType.PEDESTRIAN

    def move(self, cell: Cell) -> None:
        """
        Changes the cell the pedestrian is standing on.
        :param cell:
        :return: None
        """
        self.cell.cell_type = CellType.EMPTY
        self.cell = cell
        if self.cell.cell_type != CellType.TARGET:
            self.cell.cell_type = CellType.PEDESTRIAN

    def __str__(self):
        return f"Pedestrians {self.id} standing on {self.cell}"

    def __eq__(self, other_ped):
        return self.id == other_ped.id


class Grid:
    """
    Grid class represents a 2D array of cells.
    """

    def __init__(self, rows: int, cols: int, cells: np.ndarray = None):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        """
        super().__init__()

        # -> This is a list of numpy arrays of all the past states of
        # the grid starting from the initial state
        self.past_states = []

        self.rows: np.int = rows
        self.cols: np.int = cols
        self.time_step: np.int = 0
        if cells is None:
            self.cells = np.array([[Cell(row, column) for column in range(cols)] for row in range(rows)])
        else:
            self.cells = cells
        self.assign_neighbours()
        self.fill_distances()
        self.pedestrians = [Pedestrian(cell) for row in self.cells
                            for cell in row if cell.cell_type.value == 1]

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

    def change_cell_type(self, row: int, col: int, cell_type: CellType) -> None:
        """
        Updates the type of the cell in the give indices and
        update the pedestrians list if necessary
        :param row: row index
        :param col: column index
        :param cell_type: the new cell type
        :return: None
        """
        if self.cells[row, col].cell_type == CellType.PEDESTRIAN:
            np.delete(self.pedestrians, self.__find_pedestrian(row, col))
        elif cell_type == CellType.PEDESTRIAN:
            self.pedestrians = np.append(self.pedestrians, Pedestrian(self.cells[row, col]))

        self.cells[row, col].cell_type = cell_type

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
