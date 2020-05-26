from simulation import Simulation

# TODO: Label X and Y axes
# TODO: Change distribution to environment?
# TODO: Make pdf an instance variable instead of a method that needs to be called
# TODO: Add a separate simulation vs. visualizer (visualizer = true/false) and test it works without visualizer
# TODO: Fix 1/2 alternation of animation being hard-coded into simulation instead of handled by animation
# TODO: Add internal links and installation instructions to readme
# TODO: Add link to contagion of concern in readme
# TODO: Make it a directory/module structure with import dependencies
# TODO: Change animation.py to the file that handles animation and make a different main file
# TODO: Fix self.iterationsremaining == 1 in both animated and not animated
# TODO: Try chopping inputs in half
# TODO: Measure impact of noise on how reactive you have to be << This could be big
# TODO: Make setting for saving anim vs showing it

def main():
    run_results = []
    for reactivity_ratio in range(1, 100):
        sim = Simulation(animate = True, reactivity_ratio = reactivity_ratio)
        sim.start()
        run_results.append([reactivity_ratio, sim.processor.survival_rate()])
        best_run = sorted(run_results, key = lambda x: x[-1])[-1]
        print(best_run)
        if best_run[-1] > 0.95:
            break
    print(run_results)

if __name__ == '__main__':
    main()