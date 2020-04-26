import enum

import numpy as np
import pyglet
from neat import DefaultGenome
from neat.genome import DefaultGenomeConfig
from shapely.geometry import Polygon, Point

from .best_player_keep import load_player_data

WIDTH = 1400
HEIGHT = 800
BLACK = 0, 0, 0, 255
RED = 255, 0, 0, 255

NODE_HALF_WIDTH = 20
NODE_BOUNDS = [-NODE_HALF_WIDTH, -NODE_HALF_WIDTH, NODE_HALF_WIDTH, NODE_HALF_WIDTH]
NODE_BOX = np.array(NODE_BOUNDS * 2) * [1, 1, -1, 1, -1, -1, 1, -1]

INPUT_NODE_COLOR = 250, 150, 150
HIDDEN_NODE_COLOR = 180, 180, 220
OUTPUT_NODE_COLOR = 150, 250, 150
NODE_NAMES = {
    0: 'FWD', 1: 'BACK', 2: 'LEFT', 3: 'RIGHT',
    -1: 'dt', -2: '+90', -3: '+60', -4: '+30', -5: '+15',
    -6: 'ZERO', -7: '-15', -8: '-30', -9: '-60', -10: '-90'
}

CONN_COLOR = 20, 20, 30
NEG_CONN_COLOR = 255, 20, 30


def get_name(key):
    return NODE_NAMES.get(key) or str(key)


def show_from(file_name):
    players = load_player_data(file_name)
    for pl in players:
        print('Genome: {}, fitness: {:.0f}'.format(pl.genome.key, pl.fitness))
    print('-----------------------------------')
    genome_key = input('Select genome: ')
    if genome_key:
        available_keys = [str(data.genome.key) for data in players]
        if genome_key in available_keys:
            data = players[available_keys.index(genome_key)]
            network = NetworkData(data.genome, data.config.genome_config)
            NetworkWindow(network).start()
        else:
            print('genome not found:', genome_key)
    print('exit')


class NodeType(enum.Enum):
    Input = 1
    Hidden = 2
    Output = 3


class NetworkData:
    def __init__(self, genome: DefaultGenome, config: DefaultGenomeConfig):
        self.key = genome.key
        self.nodes = [NetworkNode.create_input_node(key) for key in config.input_keys]
        for key, node in genome.nodes.items():
            if key in config.output_keys:
                self.nodes.append(NetworkNode.create_node(node, NodeType.Output))
            else:
                self.nodes.append(NetworkNode.create_node(node, NodeType.Hidden))
        self.connections = [NetworkConnection(conn) for conn in genome.connections.values()]


class NetworkNode:
    @staticmethod
    def create_input_node(key):
        return NetworkNode(key, 0, 0, NodeType.Input)

    @staticmethod
    def create_node(node, type):
        return NetworkNode(node.key, node.bias, node.response, type)

    def __init__(self, key, bias, response, node_type: NodeType):
        self.key, self.bias, self.response, self.type = key, bias, response, node_type

    def __str__(self):
        return '{} node {:4} (bias: {:3.2f}, response: {:3.2f})'.format(
            self.type.name, get_name(self.key), self.bias, self.response)


class NetworkConnection:
    def __init__(self, conn):
        (self.input, self.output), self.weight, self.enabled = conn.key, conn.weight, conn.enabled

    def __str__(self):
        return 'Connection {:4}->{:4} (weight: {:3.2f}, enabled: {})'.format(
            get_name(self.input), get_name(self.output), self.weight, self.enabled)


class NetworkWindow(pyglet.window.Window):
    def __init__(self, data: NetworkData):
        super().__init__(WIDTH, HEIGHT, caption='Network {}'.format(data.key))
        self.set_location(0, 0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.batch = pyglet.graphics.Batch()
        input_count = len(list(filter(lambda __node: __node.type == NodeType.Input, data.nodes)))
        hidden_count = len(list(filter(lambda __node: __node.type == NodeType.Hidden, data.nodes)))
        output_count = len(list(filter(lambda __node: __node.type == NodeType.Output, data.nodes)))
        node_xs, node_ys = [0, 0, 0], [HEIGHT - 50, HEIGHT // 2, 50]
        deltas = [WIDTH / (cnt + 1) for cnt in [input_count, hidden_count, output_count]]
        color_map = [INPUT_NODE_COLOR, HIDDEN_NODE_COLOR, OUTPUT_NODE_COLOR]
        ix_map = {NodeType.Input: 0, NodeType.Hidden: 1, NodeType.Output: 2}

        self.nodes = []
        self.edit_node_ix = -1
        for node in data.nodes:
            type_ix = ix_map[node.type]
            node_xs[type_ix] += deltas[type_ix]
            x, y = node_xs[type_ix], node_ys[type_ix]
            self.nodes.append(NodeGraphics(self.batch, x, y, node, color_map[type_ix]))
        self.connections = []
        for conn in data.connections:
            if conn.enabled:
                in_node = find_node(self.nodes, conn.input)
                out_node = find_node(self.nodes, conn.output)
                self.connections.append(ConnectionGraphics(self.batch, in_node, out_node, conn))

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        pyglet.app.run()

    def update(self, dt):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if self.edit_node_ix >= 0:
            self.edit_node_ix = -1
        else:
            for ix, node in enumerate(self.nodes):
                if node.collision.contains(Point(x, y)):
                    self.edit_node_ix = ix

    def on_mouse_motion(self, x, y, dx, dy):
        if self.edit_node_ix >= 0:
            self.nodes[self.edit_node_ix].set_position(x, y)

    def on_draw(self):
        self.clear()
        for conn in self.connections:
            conn.draw()
        for node in self.nodes:
            node.draw()
        self.batch.draw()


class NodeGraphics:
    def __init__(self, batch, x, y, node: NetworkNode, bg_color):
        self.key, self.x, self.y = node.key, 0, 0
        self.vertices, self.collision = [], Polygon()
        self.bg_color = ('c3B', bg_color * 4)
        self.color = ('c4B', BLACK * 4)
        self.callbacks = []

        self.name_lbl = pyglet.text.Label(
            get_name(node.key), anchor_x='center', anchor_y='center', color=BLACK, font_size=10, batch=batch)
        self.bias_lbl = pyglet.text.Label(
            'b:{:.2f}'.format(node.bias) if node.bias else '',
            color=BLACK if node.bias > 0 else RED,
            anchor_x='left', anchor_y='center', font_size=10, batch=batch)
        self.response_lbl = pyglet.text.Label(
            'r:{:.2f}'.format(node.response) if node.response else '',
            color=BLACK if node.response > 0 else RED,
            anchor_x='center', anchor_y='top', font_size=10, batch=batch)
        self.set_position(x, y)

    def set_position(self, x, y):
        self.x, self.y = x, y
        bounds = []
        pos, pos_ix = (x, y), 0
        for coord in NODE_BOX:
            bounds.append(coord + pos[pos_ix])
            pos_ix = 0 if pos_ix else 1
        self.vertices = ('v2f', bounds)
        self.collision = Polygon(np.reshape(bounds, (-1, 2)))
        self.name_lbl.x = self.response_lbl.x = x
        self.name_lbl.y = self.bias_lbl.y = y
        self.bias_lbl.x = x + NODE_HALF_WIDTH * 1.2
        self.response_lbl.y = y - NODE_HALF_WIDTH * 1.2
        for cb in self.callbacks:
            cb(x, y)

    def add_change_cb(self, callback):
        self.callbacks.append(callback)

    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON, self.vertices, self.bg_color)
        pyglet.gl.glLineWidth(2)
        pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP, self.vertices, self.color)


class ConnectionGraphics:
    def __init__(self, batch, in_node: NodeGraphics, out_node: NodeGraphics, conn: NetworkConnection):
        self.conn = conn
        use_color = CONN_COLOR if self.conn.weight > 0 else NEG_CONN_COLOR
        self.color = ('c3B', use_color * 2)
        self.line = [in_node.x, in_node.y, out_node.x, out_node.y]
        self.vertices = ('v2f', self.line)
        in_node.add_change_cb(self.create_listener(0))
        out_node.add_change_cb(self.create_listener(1))

        self.weight_lbl = pyglet.text.Label(
            'w:{:.2f}'.format(self.conn.weight),
            color=BLACK if self.conn.weight > 0 else RED,
            anchor_x='left', anchor_y='center', font_size=10, batch=batch)
        self.__update_text_pos()

    def create_listener(self, ix):
        def update_node(x, y):
            self.line[ix * 2] = x
            self.line[ix * 2 + 1] = y
            self.__update_text_pos()

        return update_node

    def __update_text_pos(self):
        self.weight_lbl.x = (self.line[0] + self.line[2]) / 2
        self.weight_lbl.y = (self.line[1] + self.line[3]) / 2

    def draw(self):
        if self.conn.enabled:
            pyglet.gl.glLineWidth(abs(self.conn.weight))
        else:
            pyglet.gl.glLineWidth(1)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINE_STRIP, self.vertices, self.color)


def find_node(nodes, key):
    for node in nodes:
        if node.key == key:
            return node
    return None
