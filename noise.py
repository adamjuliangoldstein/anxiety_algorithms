from numpy import random

class Noise:
    def __init__(self, mu = 0, sigma = 0): # Or try mu = -0.05, sigma = 0.1
        self.mu = mu
        self.sigma = sigma
    
    # Given an input ("actual") threat likelihood (from 0 to 1), add normally
    # distributed noise and generate an output ("perceived") threat likelihood
    # (also from 0 to 1):
    def adjust(self, i):
        noise = random.normal(self.mu, self.sigma)
        temp_output = i + noise
        if temp_output > 1:
            return 1
        elif temp_output < 0:
            return 0
        else:
            return temp_output