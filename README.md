# Anxiety Algorithms

Anxiety Algorithms is a Python project for simulating agents interacting with environments, where agents decide how "anxious" to be to maximize survival. This code is based on the conceptual framework of the [Anxiety Algorithms](https://www.adamjuliangoldstein.com/blog/anxiety-algorithm/) series, and in particular [The Contagion of Concern](https://www.adamjuliangoldstein.com/blog/contagion-of-concern/).

Agents encounter a sequence of "inputs" (stimuli); these represent real-life interactions. Each input has some likelihood of being a threat.

The agent may or may not perceive this threat likelihood accurately, because the agent's perception may be a) systematically biased and/or imprecise, and/or b) colored by previous experiences not representative of the threat level of the current environment. Based on the agent's *perception* of the likelihood an input is a threat, along with a parameter known as the Concern Zone, the agent decides whether to attack.

The Concern Zone is an agent's best guess of how safe something could be and still be worth attacking. A Concern Zone of 0.25 means the agent will attack anything that seems as dangerous as the 25% most dangerous things it's encountered. A Concern Zone of 0.99 means the agent attacks nearly everything, other than the 1% safest things it encounters.

After the agent decides whether to attack, it finds out whether it survived unscathed or suffered damage. If it suffered damage, the agent updates its Concern Zone. If damage came from ignoring a real threat, the Concern Zone increases; if damage came from attacking a non-threat, the Concern Zone shrinks. For reasons explained in [The Contagion of Concern](https://www.adamjuliangoldstein.com/blog/contagion-of-concern/), agents should generally increase their Concern Zone in bigger steps than they decrease it; the ratio between these values is known as the Reactivity Ratio.

With appropriate calibration of the Reactivity Ratio, this process results in agents achieving near-optimal rates of survival, even when the agents' perceptions are biased and/or inaccurate and/or the environment is rapidly changing.

This code 

## Usage

```python animation.py```

## Contributing
Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)