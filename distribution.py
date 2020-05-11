import math
import random

class Distribution:
    # This class represents the distribution of threat likelihoods.
    # The distribution is assumed to linearly increase or decrease
    # and the slope of the pdf given by a.
    # If a is 0, the distribution is uniform.
    # If a > 0, the distribution is skewed towards more dangerous things.
    # If a < 0, the distribution is skewed towards safer things.
    min_a = -2
    max_a = 2
    max_y = max(abs(min_a), abs(max_a))
    
    def __init__(self, a = None):
        if a != None: # If a is specified, use it
            self.a = a
        else: # Otherwise pick a at random
            self.a = random.uniform(self.min_a, self.max_a)
    
    def pdf(self):
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
        b = 1 - (self.a / 2)
        return lambda T: self.a*T + b
    
    def cdf(self):
        # From prior function, F(T) = (a/2)*T^2 + b*T
        b = 1 - (self.a / 2)
        return lambda T: (self.a / 2)*(T**2) + b*T
    
    def inv_cdf(self):
        if self.a == 0:
            return lambda x: x
        else:
            # f(T) = a*T + 1 - (a/2)
            # cdf(T) = integral(f(T)) = (a/2)*T^2 + (1 - (a/2))*T
            # So cdf^-1(x) is given by quadratic equation:
            return lambda x: (1 / (2*self.a))*((self.a - 2.0) +
                                               math.sqrt(self.a**2 +
                                                       8*self.a*x -
                                                       4*self.a + 4))
         
    # Pull an item (i.e. a threat likelihood) from my pdf
    def generate_likelihood(self):
        # To ensure it's weighted appropriately, use the inverse cdf:
        return self.inv_cdf()(random.random())

    # Compute Paranoia Line from Concern Coefficient within this distribution
    def c_to_p(self, c):
        return self.inv_cdf()(c)
    
    # Compute Concern Coefficient from Paranoia Line within this distribution
    def p_to_c(self, p):
        return self.cdf()(p)