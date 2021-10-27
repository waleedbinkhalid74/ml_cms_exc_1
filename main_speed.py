from utilities_speed import scenario_loader, scenario_builder
import game_gui_speed

YELLOW = '\033[93m'
ENDC = '\033[0m'


def crowd_simulator():
    print(f"{YELLOW} Leave answers empty for default {ENDC}")
    load_scenario_bool = input("Do you want to load a scenario? (y/n)")
    # Case if the user wishes to load a scenario saved in the scenario directory.
    if load_scenario_bool == 'y':
        scenario = scenario_loader()
    elif load_scenario_bool == 'n':
        scenario = scenario_builder()
    else:
        scenario = scenario_builder()
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

    game_gui_speed.start_game_gui(scenario, max_steps=max_steps, dijkstra=dijkstra)


def main():
    crowd_simulator()


if __name__ == "__main__":
    main()
