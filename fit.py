import numpy as np
import scipy.interpolate as spi
import matplotlib.pyplot as plt

def fitting(x):
    input_x = np.arange(5, 85, 5)
    y = [0.75, 1.23, 1.48, 1.65, 1.60, 1.55, 1.51, 1.49, 1.45, 1.42, 1.34, 1.25, 1.17, 1.05, 0.93, 0.67]
    output_y = np.array(y)
    coeff = spi.splrep(input_x, output_y, k=3)
    y_app = spi.splev(x, coeff)
    return y_app


# input_x = np.arange(5, 85, 5)
# y = [0.75, 1.19, 1.48, 1.62, 1.58, 1.55, 1.50, 1.49, 1.46, 1.42, 1.34, 1.25, 1.17, 1.05, 0.93, 0.68]
# output_y = np.array(y)

# # print(len(y))
# # print(input_x.shape)
# x_new = np.arange(5,80, 1)

# iy3 = fitting(x_new)

# fig=plt.figure(num=1,figsize=(6,4))

# x_ticks = np.arange(0, 80, 10)

# y_ticks = np.arange(0, 3, 0.5)


# plt.xticks(x_ticks)
# plt.yticks(y_ticks)

# plt.plot(x_new, iy3)
# plt.show()