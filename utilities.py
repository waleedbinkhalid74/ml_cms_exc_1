import os
from os import listdir
from os.path import isfile, join
from shutil import copyfile

from game_gui import start_game_gui
from grid_structure import *


def parser_array2obj(array, obstacle_avoidance: bool = True) -> Grid:
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

    :param obstacle_avoidance: if false, all obstacles are ignored
    :param array: scenario in numpy array format
    :return: Grid object
    """
    assert len(array.shape) == 2, f"The array to grid parser expects 2D array, given {array.shape}"
    cells = np.array([[Cell(row, column, CellType(array[row, column]), obstacle_avoidance=obstacle_avoidance)
                       for column in range(array.shape[1])]
                      for row in range(array.shape[0])])
    grid = Grid(array.shape[0], array.shape[1], cells)
    grid_valid, error_msg = grid.is_valid()
    assert grid_valid, error_msg
    return grid


def scenario_loader():
    """
    This is a helper function that asks if the user wishes to load an existing scenario or design their own scenario.
    If a pre-existing scenario is loaded, the function calls the parser to construct the class structure out of the
    saved scenario file.
    Otherwise the control is handed over to the scenario builder function that helps the user in constructing a new
    scenario.

    :return: Grid object, cell size meters in float
    """
    # Get the names of the available scenario files and list them nicely
    scenario_files = [f for f in listdir('scenarios') if isfile(join('scenarios', f))]
    print("Available scenario files are: ")
    for i, scenario_file in enumerate(scenario_files):
        print("Scenario", i, ": ", scenario_file)
    scenario_number = int(input("Please select which scenario you wish to load. Enter scenario id:"))
    filename = "./scenarios/" + scenario_files[scenario_number]
    # Open and read the scenario file
    with open(filename, newline='') as csvfile:
        scenario = np.array(list(csv.reader(csvfile))).astype(int)
    # Display the inital state of the scenario
    print("Initial state of the loaded scenario:")
    # For some presaved scenarios the cell size is not simply 1m but different. This has been hardcoded for
    # some scenarios below
    if scenario_files[scenario_number] == "rimea_test1.csv":
        cell_size_meters = 0.4
    elif scenario_files[scenario_number] == "rimea_test6.csv":
        cell_size_meters = 0.5
    else:
        cell_size_meters = 1.0
    # cell_size_meters = float(input(
    #     "For the given scenarios please refer to the discretization table in the notebook or in the README.md file."
    #     "Please select the size of each cell in meters: "))
    # visualize_state(scenario)
    scenario = parser_array2obj(scenario)
    return scenario, cell_size_meters


def scenario_builder():
    """
    Uses PyQt5 to build a custom scenario. User has to take the following steps:
     1. Define size of grid with rows and cols
     2. Manually add P, O or T at the given cells

    :return: Grid object, cell size meters in float
    """
    # Get size of grid from user
    cell_size_meters = float(input("Please select the size of each cell in meters: "))
    print("Initial state of the scenario builder:")

    rows, cols = tuple([eval(x) for x in input("Enter the size of the grid in the format: rows, columns: ").split(',')])
    return Grid(rows, cols), cell_size_meters


def execute_rimea_4():
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_1 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_1 = parser_array2obj(rimea_4_1)
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_2 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_2 = parser_array2obj(rimea_4_2)
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_3 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_3 = parser_array2obj(rimea_4_3)
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_4 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_4 = parser_array2obj(rimea_4_4)
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_5 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_5 = parser_array2obj(rimea_4_5)
    with open('./scenarios/rimea_test4.csv', newline='') as csvfile:
        rimea_4_6 = np.array(list(csv.reader(csvfile))).astype(int)
        rimea_4_6 = parser_array2obj(rimea_4_6)

    cell_size_meters = 0.3333
    rimea_4_1.set_cell_size(0.3333)
    rimea_4_1.flood_pedestrians(1)
    rimea_4_2.set_cell_size(0.3333)
    rimea_4_2.flood_pedestrians(2)
    rimea_4_3.set_cell_size(0.3333)
    rimea_4_3.flood_pedestrians(3)
    rimea_4_4.set_cell_size(0.3333)
    rimea_4_4.flood_pedestrians(4)
    rimea_4_5.set_cell_size(0.3333)
    rimea_4_5.flood_pedestrians(5)
    rimea_4_6.set_cell_size(0.3333)
    rimea_4_6.flood_pedestrians(6)

    # Actual Measuring Point
    rimea_4_1.add_measuring_point(15, 5)
    rimea_4_1.add_measuring_point(15, 6)
    rimea_4_1.add_measuring_point(16, 5)
    rimea_4_1.add_measuring_point(16, 6)
    rimea_4_2.add_measuring_point(15, 5)
    rimea_4_2.add_measuring_point(15, 6)
    rimea_4_2.add_measuring_point(16, 5)
    rimea_4_2.add_measuring_point(16, 6)
    rimea_4_3.add_measuring_point(15, 5)
    rimea_4_3.add_measuring_point(15, 6)
    rimea_4_3.add_measuring_point(16, 5)
    rimea_4_3.add_measuring_point(16, 6)
    rimea_4_4.add_measuring_point(15, 5)
    rimea_4_4.add_measuring_point(15, 6)
    rimea_4_4.add_measuring_point(16, 5)
    rimea_4_4.add_measuring_point(16, 6)
    rimea_4_5.add_measuring_point(15, 5)
    rimea_4_5.add_measuring_point(15, 6)
    rimea_4_5.add_measuring_point(16, 5)
    rimea_4_5.add_measuring_point(16, 6)
    rimea_4_6.add_measuring_point(15, 5)
    rimea_4_6.add_measuring_point(15, 6)
    rimea_4_6.add_measuring_point(16, 5)
    rimea_4_6.add_measuring_point(16, 6)

    # Control Point
    rimea_4_1.add_measuring_point(15, 25)
    rimea_4_1.add_measuring_point(15, 26)
    rimea_4_1.add_measuring_point(16, 25)
    rimea_4_1.add_measuring_point(16, 26)
    rimea_4_2.add_measuring_point(15, 25)
    rimea_4_2.add_measuring_point(15, 26)
    rimea_4_2.add_measuring_point(16, 25)
    rimea_4_2.add_measuring_point(16, 26)
    rimea_4_3.add_measuring_point(15, 25)
    rimea_4_3.add_measuring_point(15, 26)
    rimea_4_3.add_measuring_point(16, 25)
    rimea_4_3.add_measuring_point(16, 26)
    rimea_4_4.add_measuring_point(15, 25)
    rimea_4_4.add_measuring_point(15, 26)
    rimea_4_4.add_measuring_point(16, 25)
    rimea_4_4.add_measuring_point(16, 26)
    rimea_4_5.add_measuring_point(15, 25)
    rimea_4_5.add_measuring_point(15, 26)
    rimea_4_5.add_measuring_point(16, 25)
    rimea_4_5.add_measuring_point(16, 26)
    rimea_4_6.add_measuring_point(15, 25)
    rimea_4_6.add_measuring_point(15, 26)
    rimea_4_6.add_measuring_point(16, 25)
    rimea_4_6.add_measuring_point(16, 26)

    # We delete the log file incase it already exists.
    if Path("./logs/measuring_points_logs.csv").exists():
        os.remove("logs/measuring_points_logs.csv")

    start_game_gui(rimea_4_1, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density1.csv")

    start_game_gui(rimea_4_2, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density2.csv")

    start_game_gui(rimea_4_3, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density3.csv")

    start_game_gui(rimea_4_4, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density4.csv")

    start_game_gui(rimea_4_5, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density5.csv")

    start_game_gui(rimea_4_6, max_steps=30, dijkstra=False, step_time=750 * cell_size_meters,
                   cell_size=cell_size_meters, periodic_boundary=True)
    copyfile("./logs/measuring_points_logs.csv", "./logs/measuring_points_logs_rimea_4_density6.csv")
