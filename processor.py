import numpy as np
from numpy import random
import bisect

class Processor:
    def __init__(self, c_guess = 0.5, chill_adjustment = 0.001,
                 reactivity_ratio = 15):
        # The perceived inputs the agent has encountered:
        self.data_seen = []
        
        # The agent's current Concern Zone guess:
        self.c_guess = c_guess
        
        # Past Concern Zone guesses:
        self.previous_c_guesses = []
        
        # How much to shrink the Concern Zone:
        self.chill_adjustment = chill_adjustment
        
        # How much faster to grow than shrink the Concern Zone:
        self.reactivity_ratio = reactivity_ratio
        self.attack_adjustment = self.chill_adjustment * reactivity_ratio
        
        self.times_surviving = 0
        self.times_dying = 0
        self.times_attacking = 0
    
    # After noise is added, the agent perceives something as having s odds of
    # being safe; should it attack?
    def does_attack(self, s):
        # If we haven't seen anything yet, choose randomly on the first one
        if len(self.data_seen) == 0:
            res = (random.random() < self.c_guess)
        else:
            # Pick the threshold output
            # Ex: if there've been 10 outputs:
            # [0.1, 0.15, 0.2, 0.22, 0.25, 0.3, 0.33, 0.7, 0.8, 0.9]
            # and c_guess = 83%,
            # then pick the 8th-most-dangerous (0.7) as the threshold
            threshold_datapoint_i = max(0, round(len(self.data_seen) *
                                                 self.c_guess) - 1)
            threshold_datapoint = self.data_seen[threshold_datapoint_i]
            # If the threat likelihood is higher than e.g. the
            # 8th-most-dangerous, then attack:
            res = (s < threshold_datapoint)
        
        # Append most recent output to the outputs seen so far, preserving sort:
        bisect.insort(self.data_seen, s)
        if res:
            self.times_attacking += 1
        return res
    
    def survives(self, did_attack):
        self.times_surviving += 1
        # Track the Concern Zone guess from this time before it's replaced
        # with a new one:
        self.previous_c_guesses.append(self.c_guess)
    
    def dies(self, did_attack):
        self.times_dying += 1
        # Track the Concern Zone guess from this time before it's replaced
        # with a new one
        self.previous_c_guesses.append(self.c_guess)
        if did_attack:
            # If we died attacking, chill a little more next time
            self.c_guess = max(0.0, self.c_guess - self.chill_adjustment)
        else:
            # If we died chilling, attack some more next time
            self.c_guess = min(1.0, self.c_guess + self.attack_adjustment)
    
    def mean_c_guess(self):
        if self.previous_c_guesses:
            return np.mean(self.previous_c_guesses)
        else:
            return self.c_guess
    
    def survival_rate(self):
        if max(self.times_surviving, self.times_dying) > 0:
            return float(self.times_surviving) / float(self.times_surviving +
                                                       self.times_dying)
        else:
            return None
    
    def attack_rate(self):
        if max(self.times_surviving, self.times_dying) > 0:
            return float(self.times_attacking) / float(self.times_surviving +
                                                       self.times_dying)
        else:
            return None