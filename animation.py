from simulation import Simulation

def main():
    run_results = []
    # Try different reactivity ratios to find the first one that results in a
    # 95% survival rate:
    for reactivity_ratio in range(1, 100):
        sim = Simulation(animate = True, reactivity_ratio = reactivity_ratio)
        sim.start()
        run_results.append([reactivity_ratio, sim.processor.survival_rate()])
        # Compute the reactivity ratio that resulted in the
        # highest survival rate:
        best_run = sorted(run_results, key = lambda x: x[-1])[-1]
        print(best_run)
        if best_run[-1] > 0.95:
            break
    print(run_results)

if __name__ == '__main__':
    main()