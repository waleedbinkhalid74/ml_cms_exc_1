from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLineEdit, QPushButton, QApplication)


class GUI(QWidget):
    def __init__(self, rows, cols):
        super().__init__()
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.rows = rows
        self.cols = cols

    def display(self):
        values = []
        values.extend(range(0,self.rows*self.cols))
        values[0] = 'P'
        values[-1] = 'T'
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        # position is an array of tuples
        # pprint("positions = " + str(positions))
        # self.setGeometry(300, 300, 300, 120)
        for position, value in zip(positions, values):
            # print("position = " + str(position))
            # print("value = " + str(value))
            if value == '':
                continue
            cell = QLineEdit(str(value))
            # setting background color to the line edit widget
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
            cell.setFixedWidth(50)
            cell.setFixedHeight(50)
            self.grid_layout.addWidget(cell, *position)
        self.setWindowTitle('Crowd Modelling: Cellular Automaton')

    def save_data(self):
        value = []
        for item in range(self.rows * self.cols):
            position = (self.grid_layout.getItemPosition(item)[0], self.grid_layout.getItemPosition(item)[1])
            if self.grid_layout.itemAt(item).widget().text() == 'P':
                value.append(1)
            elif self.grid_layout.itemAt(item).widget().text() == 'O':
                value.append(2)
            elif self.grid_layout.itemAt(item).widget().text() == 'T':
                value.append(3)
            else:
                value.append(0)
        return value
