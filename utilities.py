import numpy as np
from os import listdir
from os.path import isfile, join
from visualization import visualize_state
import csv
import sys
from PyQt5.QtWidgets import QApplication
from gui import GUI


def parser_array2obj(array):
    """
    This function converts scenarios in numpy array format the follow the following encoding:
       Array encoding rule
        0: Empty Cell
        1. Pedestrian Cell
        2. Obstacle Cell
        3. Target Cell
        All array entries must be ints or floats
    into the Class structure that is defined for our code.

    For more details on the class structure please see the report or the Class docstring.

    :param array: scenario in numpy array format
    :return: Grid object
    """
    # TODO: Convert numpy array into grid object once Qais has implemented the class structure.
    pass


def parser_obj2array(grid):
    """
    This function reads the grid object and converts it into a numpy array with following encoding
    Array encoding rule
        0: Empty Cell
        1. Pedestrian Cell
        2. Obstacle Cell
        3. Target Cell
    All array entries will be ints or floats

    For more details on the class structure please see the report or the Class docstring.

    :param grid: in Grid class format
    :return: numpy array
    """
    # TODO: Convert grid object into numpy array once Qais has implemented the class structure.
    pass


def scenario_loader():
    """
    This is a helper function that asks if the user wishes to load an existing scenario or design their own scenario.
    If a pre-existing scenario is loaded, the function calls the parser to construct the class structure out of the
    saved scenario file.
    Otherwise the control is handed over to the scenario builder function that helps the user in constructing a new
    scenario.

    :return: Grid object
    """

    # Get the names of the available scenario files and list them nicely
    scenario_files = [f for f in listdir('scenarios') if isfile(join('scenarios', f))]
    print("Available scenario files are: ")
    for i, scenario_file in enumerate(scenario_files):
        print("Scenario", i, ": ", scenario_file)
    scenario_number = int(input("Please select which scenario you wish to load. Enter scenario id:"))
    filename = "./scenarios" + scenario_files[scenario_number]
    # Open and read the scenario file
    with open('./scenarios/task_1.csv', newline='') as csvfile:
        scenario = np.array(list(csv.reader(csvfile))).astype(int)
    # Display the inital state of the scenario
    print("Initial state of the loaded scenario:")
    visualize_state(scenario)
    return scenario
    # TODO: Call parser to convert this numpy array into grid object once Qais has implemented the class structure.


def scenario_builder():
    """
    Uses PyQt5 to build a custom scenario. User has to take the following steps:
     1. Define size of grid with rows and cols
     2. Manually add P, O or T at the given cells

    :return: custom_scenario: numpy array grid with following encoding
    Array encoding rule
        0: Empty Cell
        1. Pedestrian Cell
        2. Obstacle Cell
        3. Target Cell
    All array entries will be ints or floats

    """
    # Get size of grid from user
    rows, cols = tuple([eval(x) for x in input("Enter the size of the grid in the format: rows, columns: ").split(',')])
    app = QApplication(sys.argv)
    # Create GUI object
    screen = GUI(rows, cols)
    # Display the screen
    screen.display()
    screen.show()
    app.exec_()
    # Extract the state of the GUI at the time it was closed
    custom_scenario = screen.save_data()
    # Display to the user what they have created
    visualize_state(custom_scenario)
    return custom_scenario
