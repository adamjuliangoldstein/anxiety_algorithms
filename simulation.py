from processor import Processor
from noise import Noise
from reaper import Reaper
from distribution import Distribution
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import patches
from matplotlib import ticker
import numpy as np

class Simulation:
    def __init__(self, animate = True, reactivity_ratio = 15, iterations = 5000,
                 distributions = 10):
        self.animate = animate
        
        # The processor contains the guessed Concern Zone and the logic
        # that determines whether to attack or not:
        self.processor = Processor(reactivity_ratio = reactivity_ratio)
        
        # The reaper contains the payoff matrix that determines how likely
        # the agent is to survive when it attacks or ignores a given input:
        self.reaper = Reaper()
        
        # Noise is added to "actual" input probabilities to compute
        # how likely the agent "thinks" the threat is:
        self.noise = Noise()
        
        # The distribution represents the threat level of the environment,
        # i.e. the distribution of threat likelihoods the agent encounters:
        self.distribution = Distribution()
        
        # How many frames are left in the animation:
        self.iterations_remaining = iterations 
        
        # How many frames until the environment changes:
        self.iterations_per_distribution = round(float(iterations) /
                                                 distributions)
        self.last_input = None
        if self.animate:
            # Credit for animation tutorial:
            # jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
            self.figure = plt.figure()
            ax = plt.axes(xlim = (0, 1), ylim = (0, Distribution.max_y))
            ax.xaxis.set_major_formatter(ticker.PercentFormatter(1.0))
            ax.set_yticks([])
            plt.xlabel("Likelihood of being safe")
            plt.ylabel("")#("Frequency of encountering")
        
            # The actual Paranoia Line:
            plt.axvline(x = self._actual_paranoia_line(), linewidth = 4,
                        color = 'k', alpha = 0.2, zorder = 1)
                    
            # The line showing the distribution of threats ("the environment"):
            self.dist_line, = ax.plot([], [], color = 'k', zorder = 2)
            
            # A triangle showing the actual threat likelihood of the input:
            self.input_tri = ax.scatter([], [], color = 'k', marker = 'v',
                                        zorder = 5)
            
            # A triangle showing the threat likelihood the robot perceives,
            # computed by taking the input and adding noise:
            self.after_noise_tri = ax.scatter([], [], color = 'w',
                                              marker = '^', zorder = 5)
            
            # A visual representation of the Concern Zone:
            self.attack_polygon = patches.Polygon([[0,0], [0,0], [0,0], [0,0]],
                                                  alpha = 0.5,
                                                  color = 'r',
                                                  edgecolor = None,
                                                  zorder = 3)
            
            # A visual representation of the non-Concern Zone:
            self.chill_polygon = patches.Polygon([[0,0], [0,0], [0,0], [0,0]],
                                                 alpha = 0.5,
                                                 color = 'b',
                                                 edgecolor = None,
                                                 zorder = 3)
            ax.add_patch(self.attack_polygon)
            ax.add_patch(self.chill_polygon)
            
            # If you want to track the imputed average Paranoia Line guessed
            # so far, change the alpha of this to > 0:
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
        # Set up each of the visual elements
        self.dist_line.set_data([], [])
        self.input_tri.set_offsets([0, 0])
        self.after_noise_tri.set_offsets([0, 0])
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
            # Un-comment these lines to export an animated gif of the
            # animation instead of showing it on the screen:
            # writer = animation.PillowWriter(fps = 2)
            # anim.save('output.gif', writer = writer)
            # raise
            plt.show()
        else:
            while self.iterations_remaining > 1:
                self.advance(None)
        
    def advance(self, i):
        if self.iterations_remaining == 1:
            self.end()
        
        # If it's time for a new distribution ("the environment has changed"):
        if self.iterations_remaining % self.iterations_per_distribution == 0:
            
            # Get a new random distribution:
            self.distribution = Distribution()
            if self.animate:
                X = np.linspace(0, 1, num = 2)
                Y = self.distribution.pdf()(X)
                self.dist_line.set_data(X, Y)
        
        # On odd frames of the animation, update the input and perceived input:
        if self.iterations_remaining % 2 == 1:
            self.last_input = self.distribution.generate_likelihood()
            self.after_noise = self.noise.adjust(self.last_input)
            if self.animate:
                self.input_tri.set_offsets([self.last_input, 0.1])
                self.after_noise_tri.set_offsets([self.after_noise, 0.05])
                
        # On even frames of the animation, determine how the agent reacts to
        # the perceived input, and update the Concern Zone if appropriate:
        elif self.last_input:
            
            # The chance it's a threat is given by the input
            # (actual threat level):
            is_a_threat = self.reaper.is_threat(self.last_input)
            
            # Whether to attack is given by whether the perceived risk is
            # greater  or less than the currently-guessed Paranoia Line:
            does_attack = self.processor.does_attack(self.after_noise)
            
            # The odds of survival are determined by the reaper:
            does_survive = self.reaper.does_survive(is_a_threat, does_attack)
            
            # Adjust the Concern Zone if needed:
            if does_survive:
                self.processor.survives(does_attack)
            else:
                self.processor.dies(does_attack)
                
            if self.animate:
                # Draw the Concern Zone from x = 0 to x = the implied guessed
                # Paranoia Line. The height of the Concern Zone is given by the
                # probability distribution of threats in the environment:
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
                mean_c_guess = self.processor.mean_c_guess()
                avg_p_guess = self.distribution.c_to_p(mean_c_guess)
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
              
# Things that would be nice:
# TODO: Label X and Y axes
# TODO: Fix even/odd alternation of animation being hard-coded into simulation instead of handled by animation
# TODO: Add internal links and installation instructions to readme
# TODO: Make it a directory/module structure with import dependencies
# TODO: Change animation.py to the file that handles animation and make a different main file
# TODO: Measure impact of noise on how reactive you have to be
# TODO: Make setting for saving anim vs showing it