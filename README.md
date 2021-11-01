# Crowd Modelling and Simulation Excercise 1

## Setup

Initialize venv
https://docs.python.org/3/library/venv.html

```python3 -m venv .venv```

activate venv

```. .venv/bin/activate```

Install dependencies in virtual environment

```pip install -r requirements.txt```

In order to execute the Crowd Simulation
```python3 main.py```

In order to see step by step explaination refer to
```cellular_automata_exc_1.ipynb```

## Introduction to GUI

To visualize the simulation of crowds in a good way, we set up a GUI. You can choose to load some given scenarios to simulate crowds or 
set up your own scenarios at will.


If you choose a given scenario, you need answer the following questions by input from command line.
Firstly, you need to input y to load a given scenario

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question1.jpg)

Seconly, you need to select a scenario number from the given list

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question2.jpg)

Next, please choose to use Dijkstra algorithm or not

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_quetion3.jpg)

Finally, determine a mamximum steps for simulation

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question4.jpg)

After that, you can see a loaded scenario on you screen. Please choose start button to begin your simulation. Also you can choose pause button while simulating to check each step.

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/Given_scenariojpg.jpg)

If you would like to set up your own scenario, you need to input n for the first question.

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question1.jpg)

Next, please set up the size of cells like 1, 0.5, 2 representing the length of a cell

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question5.jpg)

Thirdly, choose the size of grids like 10,10

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question6.jpg)

Next, determine to use Dijkstra algorithm or not

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_quetion3.jpg)

Finally, set up a maximum steps for simulation

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/y_question4.jpg)

After that, you can get a GUI interface. You can choose to set up locations and numbers of pedestrians, targets, obstacles at will by left clicking the cell. Please choose start button to begin your simulation. Also you can choose pause button while simulating to check each step

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/your_own_scenario.jpg)


