import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from matplotlib import animation
from scipy import stats

MIN_A = -1
MAX_A = 1
#NOISE_MU = -0.05
NOISE_MU = 0
#NOISE_SIGMA = 0.1
NOISE_SIGMA = 0
FRAMES_PER_ANIMATION = 2500

global attack_adjustment, chill_adjustment, run_results

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
    # Sort run_results so the best-performing experiment is first
    sorted_run_results = sorted(run_results, key = lambda x: -x[-1])
    return sorted_run_results[0]

def _best_run_chill_adjustment():
    return _best_run()[0]

def _best_run_attack_adjustment():
    return _best_run()[1]
    
def new_chill_adjustment():
    candidate = _best_run_chill_adjustment() + random.normal(0, 0.025)
    if candidate < 0:
        return 0
    elif candidate > 1:
        return 1
    else:
        return candidate
        
def new_attack_adjustment():
    candidate = _best_run_attack_adjustment() + random.normal(0, 0.025)
    if candidate < 0:
        return 0
    elif candidate > 1:
        return 1
    else:
        return candidate

def init():
    global line, new_input, new_output, guess_line, counter, inv_cdf, guessed_pl
    line.set_data([], [])
    new_input.set_offsets(np.c_[0, 0])
    new_output.set_offsets(np.c_[0, 0])
    guess_line.set_data([guessed_pl, guessed_pl], [0, max_y])
    return line, new_input, new_output, guess_line

def animate(i):
    global line, new_input, new_output, guess_line
    global counter, inv_cdf, guessed_pl, last_input, last_output
    global times_surviving, encounters
    if i == FRAMES_PER_ANIMATION - 1:
        plt.close(fig)
        print("Chill adjustment:", chill_adjustment, "Attack adjustment:", attack_adjustment, "Survivals: ", float(times_surviving) / encounters)
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
        is_a_threat = (random.random() < last_input)
        # Whether to attack is given by the risk we perceive is greater or
        # less than the currently-guessed Paranoia Line
        will_attack = (last_output < guessed_pl)
        will_survive = survives(is_a_threat, will_attack)
        # Adjust the guessed paranoia line depending on whether
        # Things are safer or not than we expected:
        if will_survive:
            times_surviving += 1
            guessed_pl = guessed_pl - chill_adjustment
        else:
            guessed_pl = guessed_pl + attack_adjustment
        guess_line.set_data([guessed_pl, guessed_pl], [0, max_y])
    counter += 1
    return line, new_input, new_output, guess_line

run_results = []
chill_adjustment = 0.05
attack_adjustment = 0.05
while True:
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
    counter = 0
    inv_cdf = None
    guessed_pl = 0.5
    last_input = None
    last_output = None
    times_surviving = 0
    encounters = 0
    anim = animation.FuncAnimation(fig, animate, init_func = init,
                                   frames = FRAMES_PER_ANIMATION,
                                   interval = 1, repeat = False, blit = True)
    plt.show()
    print(_best_run())
    chill_adjustment = new_chill_adjustment()
    attack_adjustment = new_attack_adjustment()