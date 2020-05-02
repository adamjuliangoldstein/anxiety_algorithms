from simulation import Simulation

# TODO: Label X and Y axes
# TODO: Update decision to attack in instance 0 based on weighted odds from initial c
# TODO: Get rid of unnecessary imports in this main file including np
# TODO: Do I need np._c?
# TODO: Change distribution to environment?
# TODO: Make pdf an instance variable instead of a method that needs to be called
# TODO: Add a separate simulation vs. visualizer (visualizer = true/false) and test it works without visualizer
# TODO: Check that number of new distributions per simulation is accurate
# TODO: Fix 1/2 alternation of animation being hard-coded into simulation instead of handled by animation
# TODO: Is prep_animation needed?
# TODO: Add readme
# TODO: Change animation.py to the file that handles animation and make a different main file

def main():
    run_results = []
    for reactivity_ratio in range(1, 100):
        sim = Simulation(reactivity_ratio = reactivity_ratio)
        sim.start()
        run_results.append([reactivity_ratio, sim.processor.survival_rate()])
        best_run = sorted(run_results, key = lambda x: x[-1])[-1][-1]
        print(best_run)
        if best_run > 0.95:
            break
    print(run_results)

if __name__ == '__main__':
    main()