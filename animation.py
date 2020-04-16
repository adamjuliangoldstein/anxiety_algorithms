import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import random
from scipy import stats

MIN_A = -1
MAX_A = 1

def get_distribution_f(a):
    # Define a probability density function f(T) = a*T + b,
    # where f(T) represents the relative likelihood to encounter
    # threat likelihoods 0 ≤ T ≤ 1.
    # Then the integral of f(T) from T = 0 to T = 1 must be 1:
    # F(T) = (a/2)*T^2 + b*T
    # F(1) - F(0) = 1
    # (a/2) + b = 1
    # b = 1 - (a/2)
    # So f(T) = a*T + 1 - (a/2)
    # For ease of visualization let a be in the range [-1, 1]
    b = 1 - (a / 2)
    return lambda T: a*T + b

def get_inverse_distribution_cdf(a):
    # f(T) = a*T + 1 - (a/2)
    # cdf(T) = integral(f(T)) = (a/2)*T^2 + (1 - (a/2))*T
    # cdf^-1(x):
    return lambda x: (1 / (2*a))*((a - 2.0) + np.sqrt(a**2 + 8*a*x - 4*a + 4))

# Credit for animation tutorial: https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
fig = plt.figure()
# The maximum y value possible will be found at one of the extremes of either the distribution with minimum or maximum a
max_y = max(get_distribution_f(MIN_A)(0),
            get_distribution_f(MIN_A)(1),
            get_distribution_f(MAX_A)(0),
            get_distribution_f(MAX_A)(1))
ax = plt.axes(xlim = (0, 1), ylim = (0, max_y))
# Show actual paranoia line: 
plt.axvline(x=0.91, linewidth=4, color='k')
line, = ax.plot([], [])
axes.set_ylim([0, max_y])

def init():
    line.set_data([], [])
    return line,

def animate(i):
    a = random.uniform(MIN_A, MAX_A)
    pdf = get_distribution_f(a)
    inv_cdf = get_inverse_distribution_cdf(a)
    X = np.linspace(0, 1, num = 100)
    Y = pdf(X)
    line.set_data(X, Y)
    return line,
                
# q = np.random.rand(10000)
# results = [inv_cdf(i) for i in q]
# print("a = " + str(a))
# res = np.mean(results)
# expected = (a + 6.0)/12.0
# print(res, expected, res/expected)
anim = animation.FuncAnimation(fig, animate, init_func = init, frames = 100, interval = 200, blit = True)
plt.show()