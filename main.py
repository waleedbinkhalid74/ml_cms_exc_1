import game_gui
from utilities import scenario_loader, scenario_builder

YELLOW = '\033[93m'
YELLOW = '\033[93m'
ENDC = '\033[0m'


def crowd_simulator():
    """
    Prompt the user to choose scenario builder or loader,
    then starts the game gui
    :return: None
    """
    print(f"{YELLOW} Leave answers empty for default {ENDC}")
    scenario_input_accepted = False
    # Case if the user wishes to load a scenario saved in the scenario directory.
    while not scenario_input_accepted:
        load_scenario_bool = input(f"Do you want to load a scenario? (y/n  default=n)")
        if load_scenario_bool == 'y':
            scenario_input_accepted = True
            scenario, cell_size_meters = scenario_loader()
        elif load_scenario_bool == 'n' or load_scenario_bool == '':
            scenario_input_accepted = True
            scenario, cell_size_meters = scenario_builder()
        else:
            print(f"Unacceptable Input")

    dijkstra_input_accepted = False
    while not dijkstra_input_accepted:
        dijkstra_bool = input(f"Would you like to use Dijkstra-algorithm? (y/n  default=n)")
        if dijkstra_bool == 'y':
            dijkstra_input_accepted = True
            dijkstra = True
        elif dijkstra_bool == 'n' or dijkstra_bool == '':
            dijkstra_input_accepted = True
            dijkstra = False
        else:
            print(f"Unacceptable Input")

    max_steps_input_accepted = False
    while not max_steps_input_accepted:
        max_steps = input(f"Maximum number of steps: (Positive integer  default=100)")
        if max_steps.isdigit() and int(max_steps) >= 0:
            max_steps_input_accepted = True
            max_steps = int(max_steps)
        elif max_steps == '':
            max_steps_input_accepted = True
            max_steps = 100
        else:
            print(f"Unacceptable Input")

    scenario.set_cell_size(cell_size_meters)
    step_time = int(cell_size_meters * 750)  # If the cell is of 1 meter then the average speed of 1.33 m/s
    game_gui.start_game_gui(scenario, max_steps=max_steps, dijkstra=dijkstra, step_time=step_time)


def main():
    crowd_simulator()


if __name__ == "__main__":
    main()
