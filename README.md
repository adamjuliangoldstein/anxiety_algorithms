# Anxiety Algorithms

Anxiety Algorithms is a Python project for simulating agents interacting with environments, where agents decide how "anxious" to be to maximize survival. This code is based on the conceptual framework of the [Anxiety Algorithms](https://www.adamjuliangoldstein.com/blog/anxiety-algorithm/) series, and in particular the essay entitled The Contagion of Concern.

Agents encounter a sequence of inputs; these represent real-life interactions. Each input has some likelihood of being a threat.

The agent may or may not perceive this threat likelihood accurately, because the agent's perception may be a) systematically biased and/or imprecise, and/or b) colored by previous experience that's not representative of the threat level of the current environment. Based on the agent's *perception* of the likelihood an input is a threat, the agent decides whether to attack.

After the agent decides, it finds out whether its decision resulted in damage to itself. If so, the agent updates its Concern Zone to reduce the likelihood it repeats that kind of damaging decision in the future.

With appropriate calibration of the feedback system, this process results in agents achieving near-optimal rates of survival, even when the agents' perceptions are biased and/or inaccurate and the dangerousness of the environment is rapidly changing.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)