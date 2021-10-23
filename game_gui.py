import pygame
import sys
from grid_structure import *
import utilities as ut

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (200, 0, 0)
GREEN = (0, 100, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
GRAY = (50, 50, 50)
colors = [WHITE, RED, YELLOW, GREEN]

BLOCK_SIZE = 15  # Set the size of the grid block


# def create_button(window_width, window_height, text, horz_pos, color):
#     button = pygame.Rect(horz_pos, window_height + 10, window_width // 6, 40)
#     pygame.draw.rect(SCREEN, color, button)  # draw button
#     text_surface_object = pygame.font.SysFont("Arial", 20).render(
#             text, True, BLACK)
#     text_rect = text_surface_object.get_rect(center=button.center)
#     SCREEN.blit(text_surface_object, text_rect)
#     return button


def create_button_pure(horz_pos, vert_pos, width, height, text, color):
    button = pygame.Rect(horz_pos, vert_pos, width, height)
    text_surface_object = pygame.font.SysFont("Arial", 20).render(
            text, True, BLACK)
    text_rect = text_surface_object.get_rect(center=button.center)
    pygame.draw.rect(SCREEN, color, button)  # draw button
    SCREEN.blit(text_surface_object, text_rect)
    return button


def main():

    load_input = input("Load a scenario (y/n)? ")
    if load_input == 'y' or load_input == 'yes':
        grid = ut.scenario_loader()
        columns = grid.cols
        rows = grid.rows
    else:
        width_input = input("Enter grid width: ")
        height_input = input("Enter grid height: ")
        columns = int(width_input)
        rows = int(height_input)
        grid = Grid(rows, columns)

    max_steps_input = input("Enter max steps: ")
    max_steps = int(max_steps_input)

    window_height = rows * BLOCK_SIZE if rows >= 20 else 300
    window_width = columns * BLOCK_SIZE if columns >= 20 else 300

    # initiate grid
    active = False
    steps = 0
    delay = 0
    seconds_per_step = 750

    # initiate window
    global SCREEN

    pygame.init()
    SCREEN = pygame.display.set_mode((window_width, window_height + 60))
    SCREEN.fill(BLACK)

    start_button = create_button_pure(window_width // 8, window_height + 10, window_width // 6, 40, "start", GREEN)
    stop_button = create_button_pure(5 * window_width // 8, window_height + 10, window_width // 6, 40, "stop", RED)

    row_edge = 0 if rows >= 20 else (window_height - rows * BLOCK_SIZE) // 2
    col_edge = 0 if columns >= 20 else (window_width - columns * BLOCK_SIZE) // 2

    rects = []
    for i in range(rows):
        rects.append([])
        for j in range(columns):
            rects[i].append(pygame.Rect(col_edge + j * BLOCK_SIZE, row_edge + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    while True:

        for i in range(rows):
            for j in range(columns):
                color_num = grid.cells[i, j].cell_type.value
                color = colors[color_num]
                if color_num == 0 and grid.cells[i, j].path:
                    color = GRAY
                    color_num = 4
                # Remove old color
                pygame.draw.rect(SCREEN, BLACK, rects[i][j], 0)
                # Put new color
                pygame.draw.rect(SCREEN, color, rects[i][j], 1 if color_num == 0 else 0, border_radius=1)
                # Draw borders
                pygame.draw.rect(SCREEN, WHITE, rects[i][j], 1)

        if len(grid.pedestrians) > 0 and active and steps < max_steps and pygame.time.get_ticks() >= delay:
            grid.update_grid(True)
            steps += 1
            delay = pygame.time.get_ticks() + seconds_per_step

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position

                # checks if mouse position is over the button

                if start_button.collidepoint(mouse_pos):
                    active = True
                    grid.flood_dijkstra()
                    print(f'Start was pressed')
                if stop_button.collidepoint(mouse_pos):
                    active = False
                    print(f'Stop was pressed')

                for i in range(rows):
                    for j in range(columns):
                        if not active and rects[i][j].collidepoint(mouse_pos):
                            # prints current location of mouse
                            print(f'rect {i} {j} was pressed')
                            grid.change_cell_type(i, j)

        pygame.display.update()


# TODO:
#   1. Track & Show time
#   2. Change distance parameters
#   3. Try smaller sizes & make BLOCK_SIZE proportional to the number of cells
#   4. Structure the code
#   5. Load a complete scenario

if __name__ == '__main__':
    main()
