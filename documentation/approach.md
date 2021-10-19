## Classes Required

1. Cell
	1. Attributes
		1. utility initialized to inf
		2. id
		3. position tuple/array
		4. visit status (will be useful when implementing the djikstra algorithm)
		5. type: O, E, T
	2. Methods
		1. Eucledian distance calculator
2. Pedestrian
	1. Attirbutes
		1. Position tuple/array
		2. id
		3. neighbouring cell id
3. Grid --> Composed of Cells
	1. Attributes
		1. cell matrix composed of cell objects --> constructed on initialization
		2. visited cell list (will be useful when implementing the djikstra algorithm
		3. unvisited cell list (will be useful when implementing the djikstra algorithm
	2. Methods
		1. Djikstra algo: to fill in utility

## Methods (Could also be converted to classes)
1. Visualizor/Animator

2. Helpful convertors (obj/numeric to string) --> for visualization/calculation
