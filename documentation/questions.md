## Questions Excercise 1
1. RiMEA 1:
   1. How to model pedestrian dimensions? Can we simply scale the cells eg if ped is 40 cm can we just do 40meters/0.4 and 2meters/0.4 to rescale everything such that the cell size is the size of the pedestrian
2. RiMEA task 4:
   1. 1000m x 10m is a huge grid. How to tackle this?
   2. Worksheet mentions the boundary conditions but the RiMEA test 4 does not mention any BC so hwo do we handle this.
   3. What is the fundamental diagram. Do we just graph densities against avg velocities?
   4. If the density is 6ped/m^2. Do we just split our cells into something like 16 cells?
   5. If the density if 0.5ped/m^2 then we already have 5000 pedestrians in our simulation which is extremely expensive. How do we tackle this? Moreover, do we divide each cell into 16 cells?
   6. Do we have to simulate every different density?
   7. Is it important to visualize this corridor as it is extremely long and fits in the GUI only with a scroll bar which is not nice to navigate
   8. Where is the target? Can we just add a strip of target at the right end.
3. Task 3
   1. When they cluster around a target, no pedestrian can enter the target becasue the cost of the target is too high and they just stay at their current places. Is this acceptable behavior?
      1. The remidy for thsi would be to check if the neighbour is a target and if so we ignore all costs.
   2. The trajectory of the pedestrian which are not along an exact diagonal is something like move diagonally first and then move in straight lines. This is a longer distance than a direct diagonal trajectory. Because of this they arrive at the target slightly later than the pedestrians that are in straight line of sight. Is this a problem that needs to be resolved? 
   3. For task 3 it says the pedestrians should be in a circle at 30-50m. Is this the diameter of the circle? If this is a radius does this mean we can increase the number of cells in the scenario that was given in task 2 (from 50x50 to more) considering one cell is 1m?
4. Cost function given in ws is not good. its only outputs a cost of 0.3 when pedestrians are very close. is this a typo? can we use 1/exp(r^2 - r_max ^ 2)
5. RiMEA 7
   1. Should the speed be a parameter? Can we set it to constant for all pedestrians? Should we be required to change it from the gui/cli? Moreover is it required that we are able to assign a distinct speed to each pedestrian?
   2. Is it important to assign an age etc to pedestrians?
   3. Can we assign speeds to pedestrians in a hardcoded way?
