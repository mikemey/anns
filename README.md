# Box pusher game

<table style="width: 100%;">
    <thead>
        <tr>
            <th>Manual play</th>
            <th>AI Demo</th>
            <th>Trained network</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><img src="resources/manual-run.png" width="250"/></td>
            <td><img src="resources/ai-run.gif" width="200" /></td>
            <td><img src="resources/train-run.gif" width="250" /></td>
        </tr>
    </tbody>
</table>

Requires:
- Python >3.5

Libraries used:
- [arcade](https://pypi.org/project/arcade/)
- [neat-python](https://pypi.org/project/neat-python/)
- [numpy](https://pypi.org/project/numpy/)


### Install dependencies

```bash
pip3 install -r requirements.txt
```

### Run game manually

```bash
python3 src/manual_player.py
```

### Demo auto player

```bash
python3 src/auto_player.py
```

### Train NEAT network

```bash
python3 src/training.py
```

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