from numpy import random

class Reaper:
    def __init__(self, true_positive_survival_odds = 1.0,
                       false_positive_survival_odds = 0.9,
                       true_negative_survival_odds = 1.0,
                       false_negative_survival_odds = 0.0):
        self.true_positive_survival_odds = true_positive_survival_odds
        self.false_positive_survival_odds = false_positive_survival_odds
        self.true_negative_survival_odds = true_negative_survival_odds
        self.false_negative_survival_odds = false_negative_survival_odds
    
    # Determine whether something with s odds of being safe is a threat or not
    def is_threat(self, s):
        return random.random() > s
    
    def does_survive(self, is_a_threat, does_attack):
        # Determine whether it's a true or false positive or negative, then roll
        # the dice as appropriate to determine survival
        if is_a_threat and does_attack:
            # True positive
            survival_odds = self.true_positive_survival_odds
        elif (not is_a_threat) and does_attack:
            # False positive
            survival_odds = self.false_positive_survival_odds
        elif (not is_a_threat) and (not does_attack):
            # True negative
            survival_odds = self.true_negative_survival_odds
        elif is_a_threat and (not does_attack):
            # False negative
            survival_odds = self.false_negative_survival_odds
        else:
            # Should never happen
            raise
        return random.random() < survival_odds