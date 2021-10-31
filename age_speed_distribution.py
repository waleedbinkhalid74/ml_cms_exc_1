import numpy as np
import scipy.interpolate as spi
import matplotlib.pyplot as plt

def age_speed_distribution(age: np.int):
    """
    Using cubic spline, we formed an interpolator function that takes the age as the input and returns the pedestrian
    speed.
    :param age: Age of the pedestrian
    :return: Speed of the pedestrian
    """
    if age is None:
        print("Error")
    else:
        input_x = np.arange(5, 85, 5)
        y = [0.75, 1.23, 1.48, 1.65, 1.60, 1.55, 1.51, 1.49, 1.45, 1.42, 1.34, 1.25, 1.17, 1.05, 0.93, 0.67]
        output_y = np.array(y)
        coeff = spi.splrep(input_x, output_y, k=3)
        speed = spi.splev(age, coeff)
        return speed
