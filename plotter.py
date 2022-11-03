import matplotlib.pyplot as plt
import numpy as np
rng = np.random.RandomState(0)


def GetPlot(cols):
    x = []
    x2 = []
    y = []
    y2 = []

    for i in range(0, len(cols)):
        if (i % 2 == 0):
            for j in range(0, len(cols[i].Boxes)):
                x.append(i+1)
                y.append(cols[i].Boxes[j].Price)
        else:
            for j in range(0, len(cols[i].Boxes)):
                x2.append(i+1)
                y2.append(cols[i].Boxes[j].Price)

    # plotting points as a scatter plot
    plt.scatter(x, y, label="O", color="green",
                marker="o", s=30)
    plt.scatter(x2, y2, label="X", color="red",
                marker="x", s=30)

    # x-axis label
    plt.xlabel('x - axis')
    # frequency label
    plt.ylabel('y - axis')
    # plot title
    plt.title('My scatter plot!')
    # showing legend

    # function to show the plot
    plt.show()
