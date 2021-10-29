from utilities import scenario_loader, scenario_builder
import pygame
import game_gui

YELLOW = '\033[93m'
ENDC = '\033[0m'


def crowd_simulator():
    print(f"{YELLOW} Leave answers empty for default {ENDC}")
    load_scenario_bool = input("Do you want to load a scenario? (y/n)")
    # Case if the user wishes to load a scenario saved in the scenario directory.
    if load_scenario_bool == 'y':
        scenario, cell_size_meters = scenario_loader()
    elif load_scenario_bool == 'n':
        scenario, cell_size_meters = scenario_builder()
    else:
        scenario, cell_size_meters = scenario_builder()
    #     assert False, "Incorrect input. Answer must be 'y' or 'n'. Please try again."

    load_scenario_bool = input("Would you like to use Dijkstra-algorithm? (y/n)")
    if load_scenario_bool == 'y':
        dijkstra = True
    elif load_scenario_bool == 'n':
        dijkstra = False
    else:
        dijkstra = False
    #     assert False, "Incorrect input. Answer must be 'y' or 'n'. Please try again."

    max_steps = input("Maximum number of steps: (Positive integer)")
    # Case if the user wishes to load a scenario saved in the scenario directory.
    if max_steps.isdigit() and int(max_steps) >= 0:
        max_steps = int(max_steps)
    else:
        max_steps = 100
    #     assert False, "Incorrect input. Answer must be a positive integer. Please try again."
    scenario.set_cell_size(cell_size_meters)
    step_time = int(cell_size_meters * 750) # If the cell is of 1 meter then the average speed of 1.33 m/s
    game_gui.start_game_gui(scenario, max_steps=max_steps, dijkstra=dijkstra, step_time=step_time, cell_size=cell_size_meters)


def main():
    crowd_simulator()


if __name__ == "__main__":
    main()
