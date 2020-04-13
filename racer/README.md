# Racer

#### Manual player

<p align="center">
    <img src="docs/manual-run.png" height="415"/>
</p>

#### Requirements
Python 3, 
[NEAT-Python](https://pypi.org/project/neat-python/), 
[NumPy](https://pypi.org/project/numpy/), 
[pyglet](http://pyglet.org/),
[Shapely](https://pypi.org/project/Shapely/)

#### Install dependencies

```bash
[project-root-dir] $ pip3 install -r requirements.txt
```

##### Start parameters

```bash
Parameters:
	[none] 	single-player mode
	2      	2-player mode
	demo   	demo mode
	train  	training mode
```

#### Run game manually

##### Single-player mode

```bash
[project-root-dir] $ python3 racer
```

##### 2-player mode

```bash
[project-root-dir] $ python3 racer 2
```

#### Demo auto player

Demo player, mainly used during development.
```bash
[project-root-dir] $ python3 racer demo
```

#### Train NEAT network

Start training:
```bash
[project-root-dir] $ python3 racer train
```