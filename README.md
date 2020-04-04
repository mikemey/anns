# Box pusher game

<table>
    <tbody>
        <tr></tr>
        <tr>
          <th colspan="3" align="left">Play manually</th>
          <th colspan="3" align="left">Auto player demo</th>
        </tr>
        <tr>
            <td colspan="3" align="center"><img src="resources/manual-run.png" height="320"/></td>
            <td colspan="3" align="center"><img src="resources/ai-run.gif" height="320" /></td>
        </tr>
        <tr><th colspan="6" align="left">Train NEAT network</th></tr>
        <tr>
            <td colspan="2" align="center">
                <p>Beginner</p>
                <img src="resources/train-beginner.gif" width="250"/>
            </td>
            <td colspan="2" align="center">
                <p>Advanced</p>
                <img src="resources/train-advanced.gif" width="250"/>
            </td>
            <td colspan="2" align="center">
                <p>Expert</p>
                <img src="resources/train-expert.gif" width="250"/>
            </td>
        </tr>
    </tbody>
</table>

#### Requirements
Python 3, 
[NumPy](https://pypi.org/project/numpy/), 
[NEAT-Python](https://pypi.org/project/neat-python/), 
[Arcade](https://pypi.org/project/arcade/)

#### Install dependencies

```bash
pip3 install -r requirements.txt
```

#### Run game manually

```bash
python3 src/manual_player.py
```

#### Demo auto player

A demonstration of `AutoPlayer`, mainly used during development.
```bash
python3 src/auto_player.py
```

### Train NEAT network

```bash
python3 src/training.py
[2020-04-04 09:07:32] --- START ---
[2020-04-04 09:21:40] g:    1, p/s: 350/ 1, avg: -40.5 max a/f: -40.5[   1] / -40.5[   1], gen a/b: -40.5 / -40.5 ( 4-28)
[2020-04-04 09:21:40] g:    2, p/s: 350/ 1, avg: -40.7 max a/f: -40.5[   1] / -36.4[   2], gen a/b: -40.9 / -36.4 ( 4-27)
[2020-04-04 09:21:41] g:    3, p/s: 350/ 1, avg: -40.6 max a/f: -40.5[   1] / -36.4[   2], gen a/b: -40.5 / -36.4 ( 4-25)
[2020-04-04 09:21:41] g:    4, p/s: 350/ 1, avg: -39.8 max a/f: -39.8[   4] / -14.9[   4], gen a/b: -37.2 / -14.9 ( 4-25)
...
```

#### Log message details:

| Key | Description |
|---:|---|
| **g:** | generation counter |
| **p/s:** | generation population count / species count |
| **avg:** | rolling average fitness for all generations |
| **max a/f:** | **maximum** rolling average fitness / best genome fitness <br> (with the generation # when the maximum occurred in square brackets) |
| **gen a/b:** | **current** generation average fitness / best genome fitness <br> (node - connection count of best genome in brackets) |

---
<br>

# Chatter box

Chat with 4 possible responses and **very** limited character recognition

### Start training:

Training sessions use configuration in `chatter/chatter.cfg`. Abort training/chat at any time with `Ctrl-C`

```bash
python3 chatter
```

The first time a network scores over [96, 98, 99, 99.5] percent 
of the maximum fitness, a demo chat-session will be started:

```
...
[2020-04-03 11:38:11]    11: 1, avg: 72.44 max a/f 72.44[  11] / 128.72[  10], gen a/b: 94.29 (125.54  4-26)
[2020-04-03 11:38:11]    12: 1, avg: 74.83 max a/f 74.83[  12] / 132.31[  12], gen a/b: 101.16 (132.31  4-23)
[2020-04-03 11:38:12]    13: 1, avg: 75.95 max a/f 75.95[  13] / 132.31[  12], gen a/b: 89.35 (121.04  5-28)
[2020-04-03 11:38:12]    14: 1, avg: 77.24 max a/f 77.24[  14] / 132.31[  12], gen a/b: 93.99 (125.17  4-25)

DEMO chat percent 0.96, fitness: 134.99
Wer bist du? (beenden mit 'exit')
>> _
```

#### Save network
This chat session supports saving the current network to a file with `save [filename]`.
It'll use the current directory and adds `.net` as extension (if missing).

```
DEMO chat percent 0.96, fitness: 134.99

Wer bist du? (beenden mit 'exit')
>> save first
net saved: first.net
>> _
```

#### Load network
To load a network from file, start chatter with `run [filename]` parameters:

```
python3 chatter run first.net

Wer bist du? (beenden mit 'exit')
>> _
``` 