import pygame

from grid_structure import *


def create_button(screen, horz_pos: np.int32, vert_pos: np.int32, width: np.int32, height: np.int32, text: str,
                  button_color: tuple, text_color: tuple):
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
    :return: PyGame Rect Object
    """
    button = pygame.Rect(horz_pos, vert_pos, width, height)
    text_surface_object = pygame.font.SysFont('Arial', height // 2).render(
        text, True, text_color)
    text_rect = text_surface_object.get_rect(center=button.center)
    pygame.draw.rect(screen, button_color, button)  # draw button
    screen.blit(text_surface_object, text_rect)
    return button


def start_game_gui(grid: Grid, max_steps: np.int32 = 200, step_time: np.int32 = 300,
                   dijkstra: bool = False, constant_speed: bool = True,
                   absorbing_targets: bool = True, periodic_boundary: bool = False):
    """
    This function sets up and starts a pygame gui window to simulate a grid object
    :param cell_size: cell dimension in meter
    :param grid: Grid object to simulate
    :param max_steps: Maximum number of simulation steps
    :param step_time: Duration of one step in milli-seconds
    :param dijkstra: A flag to use the Dijkstra algorithm
    :param absorbing_targets: A flag the pedestrians disappear once they reach the target
    :param periodic_boundary: A flag to make the grid an infinite loop
    :param constant_speed: A flag to make all pedestrians have the same speed
    :return: None
    """
    # Start pygame
    pygame.init()

    # Get monitor parameters
    info_object = pygame.display.Info()
    monitor_width, monitor_height = info_object.current_w, info_object.current_h

    # Define essential colors
    blue = (0, 0, 100)
    white = (200, 200, 200)
    red = (200, 0, 0)
    green = (0, 100, 0)
    yellow = (200, 200, 0)
    gray = (50, 50, 50)
    cell_colors = [white, red, yellow, green]

    # Set game window width & height
    block_size_rows = (monitor_height - 100) // (grid.rows + 1) if grid.rows >= 20 else monitor_height // 60
    block_size_cols = (monitor_width - 100) // (grid.cols + 1) if grid.cols >= 20 else monitor_width // 60
    block_size = min(block_size_rows, block_size_cols)

    side_edges = 10
    window_height = side_edges + (grid.rows + 1) * block_size if grid.rows >= 20 else monitor_height // 3
    window_width = side_edges + (grid.cols + 1) * block_size if grid.cols >= 20 else monitor_width // 3

    row_edge = side_edges // 2 if grid.rows >= 20 else (window_height - (grid.rows + 1) * block_size) // 2
    col_edge = side_edges // 2 if grid.cols >= 20 else (window_width - (grid.cols + 1) * block_size) // 2

    # Set game window
    screen = pygame.display.set_mode((window_width, window_height + 60))
    screen.fill(blue)
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
                create_button(screen, col_edge + j * block_size, row_edge, block_size, block_size, str(j), blue, white)
            elif j == 0 and i != 0:
                create_button(screen, col_edge, row_edge + i * block_size, block_size, block_size, str(i), blue, white)
            elif i != 0 and j != 0:
                rects[i - 1].append(pygame.Rect(col_edge + j * block_size, row_edge + i * block_size,
                                                block_size, block_size))

    # Set start & pause buttons
    start_button = create_button(screen,
                                 2 * window_width // 8, window_height + 10,
                                 block_size * 6, block_size * 3 // 2,
                                 "Start", green, blue)
    pause_button = create_button(screen,
                                 5 * window_width // 8, window_height + 10,
                                 block_size * 6, block_size * 3 // 2,
                                 "Pause", red, blue)

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
                pygame.draw.rect(screen, blue, rects[i][j], 0)
                # Put new color
                pygame.draw.rect(screen, color, rects[i][j], 1 if color_num == 0 else 0, border_radius=1)
                # Draw borders
                pygame.draw.rect(screen, white, rects[i][j], 1)

        # Simulate one step
        if grid.pedestrians and simulation_running and not simulation_done \
                and steps < max_steps and \
                (not constant_speed or pygame.time.get_ticks() >= step_waiting_time):
            grid.update_grid(current_time=(pygame.time.get_ticks() - simulation_start_time) - simulation_stoppage_time,
                             max_steps=max_steps, dijkstra=dijkstra,
                             absorbing_targets=absorbing_targets, constant_speed=constant_speed,
                             periodic_boundary=periodic_boundary)
            step_waiting_time = pygame.time.get_ticks() + step_time

        if grid.pedestrians:
            steps = max([ped.steps for ped in grid.pedestrians])

        # Simulation done
        if (not grid.pedestrians or steps >= max_steps) and simulation_running:
            simulation_total_time = (pygame.time.get_ticks() - simulation_start_time) - simulation_stoppage_time
            create_button(screen,
                          window_width // 10, window_height + 10,
                          8 * window_width // 10, block_size * 3 // 2,
                          f"Time = {simulation_total_time / 1000} seconds  -  "
                          f"steps = {steps}  -  "
                          f"Pedestrians Gone = {pedestrians - len(grid.pedestrians)}", green, blue)
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
                        pedestrians = len(grid.pedestrians)
                        if dijkstra:
                            grid.flood_dijkstra()
                        else:
                            grid.fill_distances()
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
