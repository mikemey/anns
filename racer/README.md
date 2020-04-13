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
loading config file: <anns/racer/training.cfg>
[2020-04-13 21:30:07] --- START ---
[2020-04-13 21:30:17] g:[    1], p/s: 75/ 2, avg:    -9 max a/f:    -9[   1] /    26[   1], gen a/b:    -9 /    26 ( 4-36)
[2020-04-13 21:30:25] g:[    2], p/s: 75/ 3, avg:    -6 max a/f:    -6[   2] /    26[   1], gen a/b:    -4 /    19 ( 4-36)
[2020-04-13 21:30:36] g:[    3], p/s: 75/ 4, avg:    -5 max a/f:    -5[   3] /    26[   1], gen a/b:    -1 /    23 ( 5-36)
[2020-04-13 21:30:47] g:[    4], p/s: 75/ 5, avg:    -2 max a/f:    -2[   4] /    33[   4], gen a/b:     7 /    33 ( 5-36)
[2020-04-13 21:31:03] g:[    5], p/s: 76/ 5, avg:     0 max a/f:     0[   5] /    33[   5], gen a/b:     8 /    33 ( 6-36)
```