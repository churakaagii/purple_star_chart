# Purple Star Chart

Generates a chart for East Asian Purple Star Astrology (aka Zi Wei Dou Shu) using an individual's birthday and based in the methods described in [The Empyrean Matrix](https://www.goodreads.com/book/show/18832563-the-empyrean-matrix) by Y.M. Lim. Both to save me typing and make this more mentally engaging, I've transformed the tabular form of information the book prefers to calculations in all but the most intransigent of derivations.

## Installation

This is very much an early-stage work in progress, so there's no real install process besides replicating the build environment. I use [Poetry](https://python-poetry.org/) while developing; if you do, just clone the repo and run `poetry install` in the directory with the `poetry.lock` file. I've also included a `requirements.txt` file if you prefer some other method.

## Usage

Right now, it's just a couple of classes:

* `src/purple_star_chart/BaZiChart.py`
  * Generates a Ba Zi Chart, aka the Four Pillars of Destiny. This is a simple form of Chinese astrology that can be entertaining on its own, but also contains information useful to generating a Purple Star Chart.
* `src/purple_star_chart/PurpleStarChart.py`

Currently, both are best initialized using provided class methods and a Gregorian calendar date and time of birth in `datetime` format from Python's standard library.

### BaZiChart Basics

For `BaZiChart.py` and a given birthday and time `dt_foo`, you can create a fully-calculated chart as an individual class instance like so:

```
from BaZiChart import BaZiChart

this_class_instance = BaZiChart.from_solar_date(dt_foo)
```

For this class only, you can send a nicely formatted version of the instance data to stdout using the following:

```
this_class_instance.pprint()
```

Separating out getting a nicely formatted string from printing said string is on the minor to-do list.

### PurpleStarChart Basics

In order to initialize an instance of `PurpleStarChart`, in addition to a birthday and time you also need to provide a gender. Unfortunately, traditional Chinese practices remain pretty insistent on a gender binary, so at the moment the only options are "male" and "female", though tweaking things to be more gender-inclusive is something I'd like to try to figure out down the line. Given  birthday and time `dt_foo` and the gender "female", you can initialize it like so:

```
from PurpleStarChart import PurpleStarChart

this_class_instance = PurpleStarChart.initialize_chart(dt_foo, "female")
```

The naming inconsistency with `BaZiChart` came from realizing while writing `PurpleStarChart` that I wanted to better separate basic class initialization from calculations required for a full chart. After getting a first pass at the base logic done, I plan to refactor and add some more flexibility in initialization and usage, and this paves the way for that. When I get to that point, I'll be bringing `BaZiChart` in line with nomenclature and behavior expectations.

## Next Steps / todo

1. Finish basic chart generation and population up to including data on star brightness as available for all 108 stars
1. Smooth out structural inconsistencies from in medias res decision-making
1. Add usability features (e.g. less constrained initialization and usage paths) and a few convience cli commands (probs via [click](https://click.palletsprojects.com/en/8.1.x/))
1. Create a basic web interface (via [Flask](https://flask.palletsprojects.com/en/3.0.x/)) and *maybe* a persistence layer
1. Add nice graphic output of finished charts
1. Add more complex logic for star placement interaction effects, etc.