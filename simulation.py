from processor import Processor
from noise import Noise
from reaper import Reaper
from distribution import Distribution
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import patches
import numpy as np

class Simulation:
    def __init__(self, animate = True, reactivity_ratio = 24, iterations = 5000,
                 distributions = 10):
        self.animate = animate
        self.processor = Processor(reactivity_ratio = reactivity_ratio)
        self.reaper = Reaper()
        self.noise = Noise()
        self.distribution = Distribution()
        self.iterations_remaining = iterations
        self.iterations_per_distribution = round(float(iterations) /
                                                 distributions)
        self.last_input = None
        if self.animate:
            # Credit for animation tutorial:
            # jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
            self.figure = plt.figure()
            ax = plt.axes(xlim = (0, 1), ylim = (0, Distribution.max_y))
        
            # The actual Paranoia Line:
            plt.axvline(x = self._actual_paranoia_line(), linewidth = 4,
                        color = 'k', alpha = 0.2, zorder = 1)
                    
            # The line showing the distribution of threats:
            self.dist_line, = ax.plot([], [], color = 'k', zorder = 2)

            self.input_tri = ax.scatter([], [], color = 'k', marker = 'v',
                                        zorder = 5)
            self.after_noise_tri = ax.scatter([], [], color = 'w',
                                              marker = '^', zorder = 5)
            self.attack_polygon = patches.Polygon([[0,0], [0,0], [0,0], [0,0]],
                                                  alpha = 0.5,
                                                  color = 'r',
                                                  edgecolor = None,
                                                  zorder = 3)
            self.chill_polygon = patches.Polygon([[0,0], [0,0], [0,0], [0,0]],
                                                 alpha = 0.5,
                                                 color = 'b',
                                                 edgecolor = None,
                                                 zorder = 3)
            ax.add_patch(self.attack_polygon)
            ax.add_patch(self.chill_polygon)
            # Show the average guess line by changing the alpha of this to > 0:
            self.avg_guess_line, = ax.plot([], [], '--', color= 'k',
                                           alpha = 0.0, zorder = 4)
    
    def _actual_paranoia_line(self):
        # The actual Paranoia Line is the threat likelihood where the odds
        # of surviving are the same whether attacking or not. This formula
        # is a more general version of the one in this footnote:
        # https://www.adamjuliangoldstein.com/blog/paranoia-parameter/#fn3
        r = self.reaper
        n = r.true_positive_survival_odds - r.false_negative_survival_odds
        d = n + r.true_negative_survival_odds - r.false_positive_survival_odds
        return n / d
    
    def prep_animation(self):
        self.dist_line.set_data([], [])
        self.input_tri.set_offsets(np.c_[0, 0])
        self.after_noise_tri.set_offsets(np.c_[0, 0])
        self.attack_polygon.set_xy([[0, 0], [0, 0], [0, 0], [0, 0]])
        self.chill_polygon.set_xy([[0, 0], [0, 0], [0, 0], [0, 0]])
        self.avg_guess_line.set_data([self.processor.mean_c_guess(),
                                      self.processor.mean_c_guess()],
                                     [0, Distribution.max_y])
        return (self.dist_line, self.input_tri, self.after_noise_tri,
                self.attack_polygon, self.chill_polygon, self.avg_guess_line)
        
    def start(self):
        if self.animate:
            anim = animation.FuncAnimation(self.figure, self.advance,
                                           init_func = self.prep_animation,
                                           frames = self.iterations_remaining,
                                           interval = 1, repeat = False,
                                           blit = True)
            plt.show()
        else:
            while self.iterations_remaining > 1:
                self.advance(None)
        
    def advance(self, i):
        if self.iterations_remaining == 1:
            self.end()
        
        # If it's time for a new distribution:
        if self.iterations_remaining % self.iterations_per_distribution == 0:
            self.distribution = Distribution()
            if self.animate:
                X = np.linspace(0, 1, num = 2)
                Y = self.distribution.pdf()(X)
                self.dist_line.set_data(X, Y)
        
        if self.iterations_remaining % 2 == 1:
            self.last_input = self.distribution.generate_likelihood()
            self.after_noise = self.noise.adjust(self.last_input)
            if self.animate:
                self.input_tri.set_offsets(np.c_[self.last_input, 0.1])
                self.after_noise_tri.set_offsets(np.c_[self.after_noise, 0.05])
        elif self.last_input:
            # The chance it's a threat is given by the input
            # (actual threat level):
            is_a_threat = self.reaper.is_threat(self.last_input)
            # Whether to attack is given by the risk we perceive is greater or
            # less than the currently-guessed Paranoia Line
            does_attack = self.processor.does_attack(self.after_noise)
            does_survive = self.reaper.does_survive(is_a_threat, does_attack)
            # Adjust the guessed paranoia line depending on whether
            # Things are safer or not than we expected:
            if does_survive:
                self.processor.survives()
            else:
                self.processor.dies()
                
            if self.animate:
                # Draw the Paranoia Line by computing it from the Concern Coefficient:
                p_guess = self.distribution.c_to_p(self.processor.c_guess)
                pdf = self.distribution.pdf()
                self.attack_polygon.set_xy([[0, 0],
                                           [0, pdf(0)],
                                           [p_guess, pdf(p_guess)],
                                           [p_guess, 0]])
                self.chill_polygon.set_xy([[p_guess, pdf(p_guess)],
                                          [p_guess, 0],
                                          [1, 0],
                                          [1, pdf(1)]])
                avg_p_guess = self.distribution.c_to_p(self.processor.mean_c_guess())
                self.avg_guess_line.set_data([avg_p_guess, avg_p_guess],
                                             [0, pdf(avg_p_guess)])
        self.iterations_remaining -= 1
        if self.animate:
            return (self.dist_line, self.input_tri, self.after_noise_tri,
                    self.attack_polygon, self.chill_polygon,
                    self.avg_guess_line)
        
    def end(self):
        plt.close(self.figure)
        print("Reactivity ratio", self.processor.reactivity_ratio,
              "Survivals: ", self.processor.survival_rate(),
              "Attacks:", self.processor.attack_rate())