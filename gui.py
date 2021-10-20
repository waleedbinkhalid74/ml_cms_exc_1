from PyQt5.QtWidgets import (QWidget, QGridLayout, QLineEdit, QPushButton, QApplication)
import numpy as np


class GUI(QWidget):
    """
    GUI class that uses PyQt5 to create a small window that the user can use to create there custom scenarios
    """
    def __init__(self, rows, cols):
        """
        Set up basic attributes for the GUI object
        :param rows: row size of grid
        :param cols: column size of grid
        """
        super().__init__()
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.rows = rows
        self.cols = cols

    def display(self):
        """
        Display the GUI with a default scenario. The first cell is set to pedestrian and the last cell is
        set to target. A middle cell is set to object so that the user knows how to manupulate the GUI.

        The cells are also colored for better visibility.
        :return: None
        """
        values = []
        values.extend(range(0,self.rows*self.cols))
        values[0] = 'P'
        values[1] = 'O'
        values[-1] = 'T'
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        # position is an array of tuples
        for position, value in zip(positions, values):
            if value == '':
                continue
            cell = QLineEdit(str(value))
            # setting background color to the line edit widget depending on the thing that occupies it.
            # pedestrian = red
            # target = green
            # object = yellow
            # empty cell = blue
            if str(value) == 'P':
                cell.setStyleSheet("QLineEdit"
                                        "{"
                                        "background : red;"
                                        "}")
            if str(value) == 'T':
                cell.setStyleSheet("QLineEdit"
                                   "{"
                                   "background : green;"
                                   "}")
            if str(value) == 'O':
                cell.setStyleSheet("QLineEdit"
                                   "{"
                                   "background : yellow;"
                                   "}")
            cell.setFixedWidth(50)
            cell.setFixedHeight(50)
            self.grid_layout.addWidget(cell, *position)
        self.setWindowTitle('Crowd Modelling: Cellular Automaton')

    def save_data(self):
        """
        Save the state of the GUI at the moment the user closes the screen. This can then be parsed and convered
        into a numpy array for visualization and further parsing purposes.
        :return: value
        """
        custom_scenario = []
        # Loop over the grid layout and store each custom_scenario
        for item in range(self.rows * self.cols):
            position = (self.grid_layout.getItemPosition(item)[0], self.grid_layout.getItemPosition(item)[1])
            if self.grid_layout.itemAt(item).widget().text() == 'P':
                custom_scenario.append(1)
            elif self.grid_layout.itemAt(item).widget().text() == 'O':
                custom_scenario.append(2)
            elif self.grid_layout.itemAt(item).widget().text() == 'T':
                custom_scenario.append(3)
            else:
                custom_scenario.append(0)
        # Reshape the GUI from 1D array to a 2D array in numpy array format
        custom_scenario = np.reshape(custom_scenario, (self.rows, self.cols))
        return custom_scenario
