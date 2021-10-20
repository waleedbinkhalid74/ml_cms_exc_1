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

    def __init__(self, row, col, cell_type=CellType.EMPTY):
        """
        Initiate the cell with the given position to an empty cell
        :param row: represents the cell position in the x-axis
        :param col: represents the cell position in the y-axis
        :param cell_type: the type of the cell
        """
        super().__init__()
        self.row = row
        self.col = col
        self.cell_type = cell_type
        self.utility = 0


class Pedestrian:
    """
    A Pedestrian has a unique cell and a unique id.
    The cell is updated after every step based on a utility function.
    """
    _id_counter = 0

    def __init__(self, cell):
        """
        Initiate the pedestrian with the given position & a unique id.
        :param cell: represents the cell where the pedestrian is standing
        """
        super().__init__()
        Pedestrian._id_counter += 1
        self.id = Pedestrian._id_counter
        self.cell = cell

    def is_valid(self):
        """
        Checks that the cell where the pedestrian is standing is occupied.
        :return: true or false
        """
        return self.cell.cell_type == CellType.PEDESTRIAN


class Grid:
    """
    Grid class represents a 2D array of cells.
    """

    def __init__(self, rows, cols, cells=None):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        """
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.pedestrians = []
        self.targets = []
        if cells is None:
            self.cells = np.array([[Cell(row, column) for column in range(cols)] for row in range(rows)])
        else:
            self.cells = cells

    def is_valid(self):
        """
        Checks if all cells in the grid are valid cells and that there are no illegal overlap
        :return: true or false with a error message
        """
        if any(not ped.is_valid() for ped in self.pedestrians):
            # print(f"Some pedestrians are standing on cells with invalid types")
            return False, "Some pedestrians are standing on cells with invalid types"
        if any(not tar.cell_type == CellType.TARGET for tar in self.targets):
            # print(f"Some targets cells have the wrong type")
            return False, f"Some targets cells have the wrong type"

        for i in range(len(self.pedestrians)):
            for j in range(i + 1, len(self.pedestrians)):
                if self.pedestrians[i].cell.row == self.pedestrians[j].cell.row and \
                        self.pedestrians[i].cell.col == self.pedestrians[j].cell.col:
                    # print(f"pedestrians {self.pedestrians[i].id} and {self.pedestrians[j].id} "
                    #       f"are standing on the same cell")
                    return False, f"pedestrians {self.pedestrians[i].id} and {self.pedestrians[j].id} " \
                                  f"are standing on the same cell"
        return True, "The grid is valid"
