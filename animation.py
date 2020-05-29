from simulation import Simulation
import sys

def run_sim(reactivity_ratio):
    run_results = []
    if reactivity_ratio:
        # If the user passed a Reactivity Ratio in the command line with -r,
        # use it
        range_start = reactivity_ratio
        range_end = range_start + 1
    else:
        # Otherwise, try every Reactivity Ratio from 1 to 100
        range_start = 1
        range_end = 100
    # Try different reactivity ratios to find the first one that results in a
    # 95% survival rate:
    for reactivity_ratio in range(range_start, range_end):
        print("Starting simulation with Reactivity Ratio", reactivity_ratio)
        sim = Simulation(animate = True, reactivity_ratio = reactivity_ratio)
        sim.start()
        run_results.append([reactivity_ratio, sim.processor.survival_rate()])
        # Compute the reactivity ratio that resulted in the
        # highest survival rate:
        best_run = sorted(run_results, key = lambda x: x[-1])[-1]
        print("The best survival so far was Reactivity Ratio",
              best_run[0], "with survival rate", best_run[-1])
        if best_run[-1] > 0.95:
            break
    print("And that's it")

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1 and args[1] == '-r':
        reactivity_ratio = int(args[2])
    else:
        reactivity_ratio = None
    run_sim(reactivity_ratio)