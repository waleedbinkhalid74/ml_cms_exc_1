import ctypes

import pygame

from grid_structure import *


def create_button(screen, horz_pos: int, vert_pos: int, width: int, height: int, text: str, button_color: tuple,
                  text_color: tuple):
    """
    This function creates a pygame rectangle with text on top.
    The rectangle can be used a button
    Handling of the button action must be done within the game loop.
    :param screen: pygame window object
    :param horz_pos: the horizontal position of the top left corner of the button in pixels
    :param vert_pos: the vertical position of the top left corner of the button in pixels
    :param width: the width of the button in pixels
    :param height: the height of the button in pixels
    :param text: the text to display on the button
    :param button_color: the color of the button as an RPG tuple
    :param text_color: the color of text as an RPG tuple
    :return:
    """
    button = pygame.Rect(horz_pos, vert_pos, width, height)
    text_surface_object = pygame.font.SysFont('Arial', height // 2).render(
        text, True, text_color)
    text_rect = text_surface_object.get_rect(center=button.center)
    pygame.draw.rect(screen, button_color, button)  # draw button
    screen.blit(text_surface_object, text_rect)
    return button


def start_game_gui(grid: Grid, max_steps: int = 200, step_time: int = 750, dijkstra=False):
    """
    This function sets up and starts a pygame gui window to simulate a grid object
    :param grid: Grid object to simulate
    :param max_steps: Maximum number of simulation steps
    :param step_time: Duration of one step in milli-seconds
    :return: None
    """
    # Get monitor parameters
    # user32 = ctypes.windll.user32
    # monitor_width, monitor_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    # Start pygame
    pygame.init()

    infoObject = pygame.display.Info()
    monitor_width, monitor_height = infoObject.current_w, infoObject.current_h
    # Define essential colors
    black = (0, 0, 0)
    white = (200, 200, 200)
    red = (200, 0, 0)
    green = (0, 100, 0)
    yellow = (200, 200, 0)
    gray = (50, 50, 50)
    cell_colors = [white, red, yellow, green]

    # Set game window width & height
    block_size = (monitor_height - 100) // (grid.rows + 1) if grid.rows >= 20 else monitor_height // 60

    side_edges = 10
    window_height = side_edges + (grid.rows + 1) * block_size if grid.rows >= 20 else monitor_height // 3
    window_width = side_edges + (grid.cols + 1) * block_size if grid.cols >= 20 else monitor_width // 3

    row_edge = side_edges // 2 if grid.rows >= 20 else (window_height - (grid.rows + 1) * block_size) // 2
    col_edge = side_edges // 2 if grid.cols >= 20 else (window_width - (grid.cols + 1) * block_size) // 2


    # Set game window
    screen = pygame.display.set_mode((window_width, window_height + 60))
    screen.fill(black)
    pygame.display.set_caption("Cellular Automata")
    game_window_icon = pygame.image.load('icons/crowd.png')
    pygame.display.set_icon(game_window_icon)

    # Create gui grid squares
    rects = []
    for i in range(grid.rows + 1):
        if i > 0:
            rects.append([])
        for j in range(grid.cols + 1):
            if i == 0 and j != 0:
                create_button(screen, col_edge + j * block_size, row_edge, block_size, block_size, str(j), black, white)
            elif j == 0 and i != 0:
                create_button(screen, col_edge, row_edge + i * block_size, block_size, block_size, str(i), black, white)
            elif i != 0 and j != 0:
                rects[i - 1].append(pygame.Rect(col_edge + j * block_size, row_edge + i * block_size,
                                                block_size, block_size))

    # Set start & pause buttons
    start_button = create_button(screen,
                                 2 * window_width // 8, window_height + 10,
                                 block_size * 6, block_size * 3 // 2,
                                 "Start", green, black)
    pause_button = create_button(screen,
                                 5 * window_width // 8, window_height + 10,
                                 block_size * 6, block_size * 3 // 2,
                                 "Pause", red, black)

    # Initial settings
    steps = 0
    simulation_running = False
    simulation_start = False
    simulation_done = False
    simulation_start_time = 0
    simulation_pause_time = 0
    simulation_stoppage_time = 0
    step_waiting_time = 0
    simulation_total_time = 0

    # Game loop
    game_gui_running = True
    while game_gui_running:

        # Draw the grid
        for i in range(grid.rows):
            for j in range(grid.cols):
                color_num = grid.cells[i, j].cell_type.value
                color = cell_colors[color_num]
                if color_num == 0 and grid.cells[i, j].path:
                    color = gray
                    color_num = 4
                # Remove old color
                pygame.draw.rect(screen, black, rects[i][j], 0)
                # Put new color
                pygame.draw.rect(screen, color, rects[i][j], 1 if color_num == 0 else 0, border_radius=1)
                # Draw borders
                pygame.draw.rect(screen, white, rects[i][j], 1)

        # Simulate one step
        if grid.pedestrians and simulation_running \
                and steps < max_steps and pygame.time.get_ticks() >= step_waiting_time:
            grid.update_grid(dijkstra=dijkstra)
            steps += 1
            step_waiting_time = pygame.time.get_ticks() + step_time

        # # Check if the simulation is done
        # if len(grid.pedestrians) == 0 and simulation_running:
        #     simulation_running = False
        #     show_results = True

        if len(grid.pedestrians) == 0 and simulation_running:
            simulation_total_time = (pygame.time.get_ticks() - simulation_start_time) - simulation_stoppage_time
            create_button(screen,
                          window_width // 8, window_height + 10,
                          6 * window_width // 8, block_size * 3 // 2,
                          f"Time = {simulation_total_time / 1000} seconds     steps = {steps}", green, black)
            simulation_running = False
            simulation_done = True

        # Handle events
        for event in pygame.event.get():

            # Close button
            if event.type == pygame.QUIT:
                pygame.quit()
                if simulation_done:
                    return simulation_total_time, steps
                else:
                    return (pygame.time.get_ticks() - simulation_start_time) - simulation_stoppage_time, steps

            # Handle pressing a button
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position

                # Start simulation
                if not simulation_done and start_button.collidepoint(mouse_pos):
                    simulation_running = True
                    if not simulation_start:
                        simulation_start_time = pygame.time.get_ticks()
                    else:
                        simulation_stoppage_time += pygame.time.get_ticks() - simulation_pause_time
                    simulation_start = True

                # Pause simulation
                if not simulation_done and pause_button.collidepoint(mouse_pos):
                    simulation_running = False
                    simulation_pause_time = pygame.time.get_ticks()

                # Handle pressing on cells (Update cell type)
                for i in range(grid.rows):
                    for j in range(grid.cols):
                        if not simulation_running and not simulation_done and \
                                rects[i][j].collidepoint(mouse_pos):
                            grid.change_cell_type(i, j)

        pygame.display.update()

# TODO:
#   1. Track & Show Number of steps & Real time
#   2. Default values for initialization questions
