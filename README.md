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
```cellular_automata_exc_1.ipynb``

##Introduction to GUI

To visualize the simulation of crowds in a good way, we set up a GUI. You can choose to load some given scenarios to simulate crowds or 
set up your own scenarios at will.


If you choose a given scenario, you need answer the following questions by input from command line.
Firstly, you need to input y to load a given scenario

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/y_question1.jpg?token=AWEFHK2RQJD6YMHVUZER3GLBPZE3M)

Seconly, you need to select a scenario number from the given list

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/y_question2.jpg?token=AWEFHK4VD2BBQMX6LL3AIZTBPZE5U)

Next, please choose to use Dijkstra algorithm or not

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/y_quetion3.jpg?token=AWEFHK6RV5OYZ2VPZU7PDD3BPZE6Y)

Finally, determine a mamximum steps for simulation

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/y_question4.jpg?token=AWEFHKYS6S3VG3Y4J3P6UA3BPZFAC)

After that, you can see a loaded scenario on you screen. Please choose start button to begin your simulation. Also you can choose pause button while simulating to check each step

![Image text](https://github.com/waleedbinkhalid74/ml_cms_exc_1/blob/develop/figures/Given_scenariojpg.jpg)

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/GUI_interface.jpg?token=AWEFHKZX76WTRXSBPKVQDPLBPZDLQ)

![Image text](https://raw.githubusercontent.com/waleedbinkhalid74/ml_cms_exc_1/develop/figures/PyGame_grid.png?token=AWEFHK6GPEBKBQULUOA5RUDBPZB6Y)
