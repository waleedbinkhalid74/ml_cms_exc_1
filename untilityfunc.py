from grid_structure import *



def untilityfunc(grid, interactions=False):

    """ 
    This function helps us update the cell states
    Update rules:
    1.If there is a target around a pedestrian, pedestrian wait here.
    2.Otherwise, calculate the distance between neighbors of a pedestrian and all targets
    Choose the neighbor with smallest distance from targets and let the pedestrian go there.
    3.Change the cell state. The cell which teh pedestrian leave from turns empty. The cell which
    the pedestrian go to turns pedestrian.

    :param: grid->Grid Class
    :param: interactions (If interactions = True, this model consider the interactions between people)
    """
    pedestrians = grid.pedestrians
    targets = grid.targets
    cells = grid.cells

    ### get indices of all targets and store them in a list
    targets_indices = []
    for target in targets:
        targets_index = [target.row, target.col]
        targets_indices.append(targets_index)

    ##update rules
    for num, pedestrian in enumerate(pedestrians):

        straight_neighbours = pedestrian.cell.straight_neighbours
        diagonal_neighbours = pedestrian.cell.diagonal_neighbours
        neighbors_indices = straight_neighbours + diagonal_neighbours

        ##flage helps us jump from a loop, if there is a target around a pedestrian
        flag = True
        ##define the smallest distance is approximately infinite
        dis_min = 10e6

        for x, y in neighbors_indices:
            ##If any neighbor of a pedestrian is a target, current state remains unchanged
            if  cells[x][y].cell_type == CellType.TARGET:
                flag = False
                break
        
        if flag:
            for x,y in neighbors_indices:
                coordx, coordy= None, None
                for i, j in targets_indices:
                    if interactions:
                        pass

                    pedestrian.cell.distance_to_target = get_distance(x,y,i,j)##how to define coordinates x,y. Are they same as indices?
                    ##if we find a smaller distance and store it in dis_min and store the corresponding indices.
                    if pedestrian.cell.distance_to_target < dis_min:
                        dis_min = pedestrian.cell.distance_to_target
                        coordx, coordy = x, y
            pedestrian.move(grid.cells[coordx][coordy])
            grid.get_current_state()

def get_distance(x,y,i,j):
    """
    :param: x, y, i, j. (x,y) is the coordinate of a pedestrian and (i,j) is the coordinate of a target
    """
    return ((x-i)**2 + (y-j)**2)**0.5

    
    


