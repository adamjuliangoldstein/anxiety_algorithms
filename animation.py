import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy import stats
import bisect

MIN_A = -2
MAX_A = 2
#NOISE_MU = -0.05
NOISE_MU = 0
#NOISE_SIGMA = 0.1
NOISE_SIGMA = 0
FRAMES_PER_ANIMATION = 5000

global attack_adjustment, chill_adjustment, run_results, outputs_seen

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

def get_distribution_cdf(a):
    # From prior function, F(T) = (a/2)*T^2 + b*T
    b = 1 - (a / 2)
    return lambda T: (a / 2)*(T**2) + b*T

def get_inverse_distribution_cdf(a):
    if a == 0:
        return lambda x: x
    else:
        # f(T) = a*T + 1 - (a/2)
        # cdf(T) = integral(f(T)) = (a/2)*T^2 + (1 - (a/2))*T
        # cdf^-1(x):
        return lambda x: (1 / (2*a))*((a - 2.0) +
                                      np.sqrt(a**2 + 8*a*x - 4*a + 4))

def p_from_c(c, a):
    # Compute Paranoia Line from Concern Coefficient
    return get_inverse_distribution_cdf(a)(c)

def c_from_p(p, a):
    # Compute Concern Coefficient from Paranoia Lina
    return get_distribution_cdf(a)(p)

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

# Determine whether it's a true or false positive or negative, then roll
# the dice as appropriate to determine survival
def survives(is_a_threat, will_attack):
    if is_a_threat and will_attack:
        # True positive
        survival_odds = 1.0
    elif (not is_a_threat) and will_attack:
        # False positive
        survival_odds = 0.9
    elif (not is_a_threat) and (not will_attack):
        # True negative
        survival_odds = 1.0
    elif is_a_threat and (not will_attack):
        # False negative
        survival_odds = 0.0
    else:
        # Should never happen
        raise
    return random.random() < survival_odds

def _best_run():
    # Sort run_results
    sorted_run_results = sorted(run_results, key = lambda x: x[-1])
    return sorted_run_results[-1]

def _best_run_chill_adjustment():
    return _best_run()[0]

def _best_run_attack_adjustment():
    return _best_run()[1]

def should_attack(new_output, c, outputs_seen):
    # If we haven't seen any outputs yet, choose randomly on the first one
    if len(outputs_seen) == 0:
        return random.choice([True, False])
    else:
        # Pick the threshold output
        # Ex: if there've been 10 outputs:
        # [0.1, 0.15, 0.2, 0.22, 0.25, 0.3, 0.33, 0.7, 0.8, 0.9]
        # and c = 83%
        # then pick the 8th-most-dangerous (0.7) as the threshold
        threshold_output_index = max(0, round(len(outputs_seen) * c) - 1)
        threshold_output = outputs_seen[threshold_output_index]
        # print(new_output, "<>", threshold_output)
        # If the threat likelihood is higher than the 8th-most-dangerous,
        # then attack
        return new_output < threshold_output
    
def new_chill_adjustment():
    candidate = _best_run_chill_adjustment() + random.normal(0, 0.05)
    if candidate < 0:
        return 0
    elif candidate > 1:
        return 1
    else:
        return candidate
        
def new_attack_adjustment():
    candidate = _best_run_attack_adjustment() + random.normal(0, 0.05)
    if candidate < 0:
        return 0
    elif candidate > 1:
        return 1
    else:
        return candidate

def _avg_guessed_c():
    if previously_guessed_cs:
        return np.mean(previously_guessed_cs)
    else:
        return 0.5

def init():
    global line, new_input, new_output, guess_line, avg_guess_line
    global counter, inv_cdf, guessed_c, a
    line.set_data([], [])
    new_input.set_offsets(np.c_[0, 0])
    new_output.set_offsets(np.c_[0, 0])
    guess_line.set_data([p_from_c(guessed_c, 0), p_from_c(guessed_c, 0)],
                        [0, max_y])
    avg_guess_line.set_data([_avg_guessed_c(), _avg_guessed_c()], [0, max_y])
    return line, new_input, new_output, guess_line, avg_guess_line

def animate(i):
    global line, new_input, new_output, guess_line, avg_guess_line
    global counter, inv_cdf, guessed_c, last_input, last_output
    global times_surviving, times_attacking, encounters, a
    if i == FRAMES_PER_ANIMATION - 1:
        plt.close(fig)
        print("Chill adjustment:", chill_adjustment, "Attack adjustment:", attack_adjustment, "Survivals: ", float(times_surviving) / encounters, "Attacks:", float(times_attacking) / encounters)
        run_results.append([chill_adjustment,
                            attack_adjustment,
                            float(times_surviving) / encounters])
    if counter % 25 == 0:
        # a = random.uniform(MIN_A, MAX_A)
        a = 0
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
        encounters += 1
        # The chance it's a threat is given by the input (actual threat level)
        is_a_threat = (random.random() > last_input)
        # Whether to attack is given by the risk we perceive is greater or
        # less than the currently-guessed Paranoia Line
        will_attack = should_attack(last_output, guessed_c, outputs_seen)
        if will_attack:
            times_attacking += 1
        will_survive = survives(is_a_threat, will_attack)
        # Append most recent output to the outputs seen so far, preserving sort:
        bisect.insort(outputs_seen, last_output)
        previously_guessed_cs.append(guessed_c)
        # Adjust the guessed paranoia line depending on whether
        # Things are safer or not than we expected:
        if will_survive:
            times_surviving += 1
            guessed_c = max(0.0, guessed_c - chill_adjustment)
        else:
            guessed_c = min(1.0, guessed_c + attack_adjustment)
        # Draw the Paranoia Line by computing it from the Concern Coefficient:
        guess_line.set_data([p_from_c(guessed_c, a),
                             p_from_c(guessed_c, a)],
                            [0, get_distribution_f(a)(p_from_c(guessed_c, a))])
        avg_guess_line.set_data([_avg_guessed_c(), _avg_guessed_c()],
                                [0, get_distribution_f(a)(_avg_guessed_c())])
    counter += 1
    return line, new_input, new_output, guess_line, avg_guess_line

chill_adjustment = 0.001
attack_adjustment = chill_adjustment*25
run_results = []
while True:
    outputs_seen = []
    previously_guessed_cs = []
    # Credit for animation tutorial: https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
    fig = plt.figure()
    # The maximum y value possible will be found at one of the extremes of 
    # either the distribution with minimum or maximum a
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
    avg_guess_line, = ax.plot([], [])
    counter = 0
    inv_cdf = None
    guessed_c = 0.5
    last_input = None
    last_output = None
    times_surviving = 0
    times_attacking = 0
    encounters = 0
    anim = animation.FuncAnimation(fig, animate, init_func = init,
                                   frames = FRAMES_PER_ANIMATION,
                                   interval = 1, repeat = False, blit = True)
    plt.show()
    print(_best_run())
    chill_adjustment = new_chill_adjustment()
    attack_adjustment = new_attack_adjustment()