import numpy as np
import pylab as plt
import random
from scipy import stats

def get_random_distribution_f():
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
    a = random.uniform(-1, 1)
    b = 1 - (a / 2)
    print(a, b)
    return lambda T: a*T + b

pdf = get_random_distribution_f()

X = np.linspace(0, 1, num = 100)
Y_dist = pdf(X)
# Y1 = X + 2*np.random.random(X.shape)
# Y2 = X**2 + np.random.random(X.shape)
# plt.scatter(X,Y1,color='k')
# plt.scatter(X,Y2,color='g')
plt.plot(X, Y_dist)
plt.axvline(x=0.91, linewidth=4, color='k')
plt.show()