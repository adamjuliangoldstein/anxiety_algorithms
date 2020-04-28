import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy import stats

MIN_A = -1
MAX_A = 1
NOISE_MU = -0.05
NOISE_SIGMA = 0.1

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

# Interpret an input with biased random noise
def process_input(i):
    noise = random.normal(NOISE_MU, NOISE_SIGMA)
    temp_output = i + noise
    if temp_output > 1:
        return 1
    elif temp_output < 0:
        return 0
    else:
        return temp_output

# Credit for animation tutorial: https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
fig = plt.figure()
# The maximum y value possible will be found at one of the extremes of either the distribution with minimum or maximum a
max_y = max(get_distribution_f(MIN_A)(0),
            get_distribution_f(MIN_A)(1),
            get_distribution_f(MAX_A)(0),
            get_distribution_f(MAX_A)(1))
ax = plt.axes(xlim = (0, 1), ylim = (0, max_y))
# Show actual paranoia line: 
plt.axvline(x = 0.91, linewidth = 4, color='k')
line, = ax.plot([], [])
new_input = ax.scatter([], [], marker = 'v')
new_output = ax.scatter([], [], marker = '^')
guess_line, = ax.plot([], [])
counter = 0
inv_cdf = None
guess_value = 0.5
last_input = None
last_output = None

def init():
    global line, new_input, new_output, guess_line, counter, inv_cdf, guess_value
    line.set_data([], [])
    new_input.set_offsets(np.c_[0, 0])
    new_output.set_offsets(np.c_[0, 0])
    guess_line.set_data([guess_value, guess_value], [0, max_y])
    return line, new_input, new_output, guess_line

def animate(i):
    global line, new_input, new_output, guess_line, counter, inv_cdf, guess_value, last_input, last_output
    if counter % 25 == 0:
        a = random.uniform(MIN_A, MAX_A)
        pdf = get_distribution_f(a)
        inv_cdf = get_inverse_distribution_cdf(a)
        X = np.linspace(0, 1, num = 100)
        Y = pdf(X)
        line.set_data(X, Y)
    if counter % 2 == 1:
        last_input = inv_cdf(random.rand())
        last_output = process_input(last_input)
        new_input.set_offsets(np.c_[last_input, 0.1])
        new_output.set_offsets(np.c_[last_output, 0.05])
    elif counter > 1:
        print(last_output)
        # TODO Update guess value based on results!
        guess_value += 0.1
        guess_line.set_data([guess_value, guess_value], [0, max_y])
    counter += 1
    return line, new_input, new_output, guess_line

# q = np.random.rand(10000)
# results = [inv_cdf(i) for i in q]
# print("a = " + str(a))
# res = np.mean(results)
# expected = (a + 6.0)/12.0
# print(res, expected, res/expected)
anim = animation.FuncAnimation(fig, animate, init_func = init, frames = 100, interval = 500, blit = True)
plt.show()