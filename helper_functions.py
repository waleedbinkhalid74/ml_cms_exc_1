import numpy as np


def document_measures(row, col, grid, cell_size, current_time, ped_id, last_steps):
    density = measure_density(row, col, grid, cell_size, current_time)
    speed = measure_speed(ped_id, last_steps, row, col, cell_size)
    measuring_points_logs = open("measuring_points_logs.txt", "w+")
    measuring_points_logs.write(f"Pedestrian {ped_id} in measuring_point ({row}, {col}) at time {current_time}"
                                f"density = {density}   speed = {speed}")
    measuring_points_logs.close()


def measure_density(row, col, grid, cell_size):
    """
    Grid class function
    :param row: the row index of the measuring point
    :param col: the column index of the measuring point
    :param grid: 2 Dimension numpy array represeting cells
    :param cell_size: The scale of cell in meters
    :return:
    """

    # Find the 10x10 square around (row,col)
    # The 10 rows are [row - 4, row + 5]
    # However, if row < 4 for example 3
    # then the rows are [0, 9]
    # and if row = 17 out of 20 rows overall in the grid
    # Then rows are [10, 19]
    # Similarly for columns

    rows = len(grid)
    cols = len(grid[row])

    row_min = row - 4 if row >= 4 else 0
    row_max = row + 5 if row + 5 < rows else rows - 1
    if rows - row_max < 5:
        row_min = 10 - (rows - row) if 10 - (rows - row) >= 0 else 0
    if row < 4:
        row_max = 9 if 9 < rows else rows - 1

    col_min = col - 4 if col >= 4 else 0
    col_max = col + 5 if col + 5 < cols else cols - 1
    if cols - col_max < 5:
        col_min = 10 - (cols - col) if 10 - (cols - col) >= 0 else 0
    if col < 4:
        col_max = 9 if 9 < cols else cols - 1

    # Count pedestrians in the square
    pedestrians_count = len([1 for r in range(row_min, row_max)
                             for c in range(col_min, col_max) if grid[r, c] == 1])

    # Scale the area according to cell_size
    measuring_area = ((row_max - row_min) * (col_max - col_min)) * (cell_size * cell_size)

    return pedestrians_count / measuring_area


def measure_speed(last_steps, cell_size):
    """
    Pedestrian class function
    :param last_steps: Array of the shape [[[row, col], time], ...]
    :param cell_size: The scale of cell in meters
    :return: The average speed over the last_steps in meter/second
    """
    # measure the covered distance by last_steps
    # Scale the distance according to cell_size
    # get the speed by dividing distance / (last_time - first_time)

    distance = 0
    time = 0
    initial_time = last_steps[0, 1]
    first_cell = last_steps[0, 0]
    for step in range(1, len(last_steps)):
        time = last_steps[step, 1] - initial_time
        if last_steps[step, 0, 0] != first_cell[0] and last_steps[step, 0, 1] != first_cell[1]:
            # diagonal step
            distance += 1.42
        else:
            # straight step
            distance += 1
        first_cell = last_steps[step, 0]
    if time > 0:
        return distance * cell_size / (time / 1000)
    else:
        return 0
