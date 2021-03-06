import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors


def visualize_state(scenario):
    """
    This function displays the state of the scenario at a certain instance.

    :param scenario: numpy array of the state of the grid. Encoding is as follows:
    Array encoding rule
        0: Empty Cell
        1. Pedestrian Cell
        2. Obstical Cell
        3. Target Cell
        All array entries must be ints or floats

    :return: None
    """

    # extract size of plot
    rows, cols = scenario.shape
    # Create color map to separately label each element on grid
    cmap = colors.ListedColormap(['blue', 'red', 'yellow', 'green'])
    bounds = [0, 1, 2, 3, 4]
    norm = colors.BoundaryNorm(bounds, cmap.N)
    fig, ax = plt.subplots(figsize=(10, 10))
    img = ax.imshow(scenario, cmap=cmap, norm=norm)
    # Make grid with x,y ticks for proper partitioning in visualization
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(0.5, cols, 1))
    ax.set_yticks(np.arange(0.5, rows, 1))
    # Add labels for a good legend
    labels = ['Empty Cell', 'Pedestrian', 'Obstical', 'Target']
    patches = [mpatches.Patch(color=cmap.colors[i], label=labels[i]) for i in range(4)]
    plt.legend(handles=patches, bbox_to_anchor=(1.1, 1.), prop={"size": 6})
    plt.tight_layout()
    fig.savefig('./figures/visuals.pdf')
