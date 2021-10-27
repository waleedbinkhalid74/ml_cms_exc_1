# Meeting Notes Excercise 1 - 18-OCt-2021

### Meeting Agenda:
1. Setup github/gitlab
2. Setup overleaf project
3. Go through worksheet and discuss tasks
4. Divide tasks and devise strategy
5. Checkout djikstra for crowds and think of how to model https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

## Meeting Notes 21-Oct-2021
1. Fix parser bug: Waleed


## Points to discuss
1. task_4 150 pedestrians too expensive to simulate
2. what is row and col in pedestrian. doesnt seem like coordinates. --> Qais?
3. rimea_1 the time from the gui is 74 seconds. this does not seem correct.
5. rimea_4 is not clear. need to ask professor --> where are the periodic bc??
4. rimea_6 some obstacles get eated away
6. rimea 7, how to give individual speeds?

### Tasks
~~1. Setup Github~~
~~2. Class structures: Qais~~
~~3. Parser csv, txt: Waleed~~
~~5. Converter from class grid to animatable grid: Waleed~~
~~4. Animation (Initial figures): Waleed~~
~~5. Divide neighbours into diagonal and straight: Yiming~~
~~6. Keep track of time by grid attribute: Yiming~~
~~7. Implement update rule: Yiming~~
~~8. Implementation of pedestrian repulsion: Yiming~~
~~9. Dijkstra algorithm: Waleed~~
~~10. Pedestrian and object: Qais~~
~~11. The cost of pedestrians should be accumulated in the normal cost of the cell(?)~~
13. Fast Marching Algo reading: Waleed, Qais, Yiming
14. Documentation: Waleed, Qais
~~15. Explaination of pedestrian interaction: Qais~~
~~2. Explaination of dijkstra~~
~~2. Explaination of rudementary obstacle avoidance: Waleed~~
    1. Explaination of update rule: Yiming
    2. Explaination of new GUI: Qais
    3. Explaination of animator: Waleed, Qais
    4. Testing: Conduct RiMEA test 1 and 4 with documentation and explaination in Latex and notebook: Yiming
    5. Testing: Conduct RiMEA test 6 and 7 with documentation and explaination in Latex and notebook: Waleed
~~16. Integrate new GUI to scenario_builder: Qais~~
~~17. Run tasks 1-4 and document in notebook and latex~~
~~18. UML diagram of the class structure: Yiming~~
15. Add operation for ignoring neighbours that are in the visited cell in dijkstra algo: Waleed
16. Add average pedestrian speed by speed=total distance by pedestrian at a certain point/current time passed: Qais
17. Add speed as a variable in pedestrian.move: Qais