from grid_structure import *

def utilityfunc(grid, interactions=False):

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
    if interactions:
        pass
    grid.update_grid()
    grid.get_current_state()


    
    


