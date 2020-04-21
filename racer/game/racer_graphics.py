from os import path

import numpy as np
import pyglet
from pyglet.graphics.vertexdomain import VertexList

from .racer_engine import PlayerState, CAR_BOUND_POINTS, CAR_BOUNDS
from .tracers import TracerLines
from .tracks import Level

resource_dir = path.join(path.abspath(path.dirname(__file__)), 'resources')
pyglet.resource.path = [resource_dir]
pyglet.resource.reindex()


def load_and_anchor_image(name, x_ratio=2, y_ratio=2):
    img = pyglet.resource.image(name)
    img.anchor_x = img.width // x_ratio
    img.anchor_y = img.height // y_ratio
    return img


car_frame_img = load_and_anchor_image('car-frame.png', x_ratio=3)
pointer_img = load_and_anchor_image('pointer.png')
box_img = load_and_anchor_image('box.png')


def random_color():
    return tuple(np.random.randint(0, 255, size=3))


def convert_data(coords, color=None, vertices_mode='v2i', color_mode='c3B'):
    pts_count = len(coords) // 2
    vertices = (vertices_mode, coords)
    color_data = (color_mode, color * pts_count) if color else None
    return pts_count, vertices, color_data


def create_vertex_list(points, color, vertices_mode='v2i', color_mode='c3B') -> VertexList:
    pts, vertices, color_data = convert_data(points, color, vertices_mode=vertices_mode, color_mode=color_mode)
    return pyglet.graphics.vertex_list(pts, vertices, color_data)


class GraphicsElement:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()

    def draw(self):
        self.batch.draw()

    def add_points(self, points, color, mode=pyglet.gl.GL_LINE_STRIP, group=None) -> VertexList:
        pts_count, vertices, color_data = convert_data(points, color)
        return self.batch.add(pts_count, mode, group, vertices, color_data)


class CarGraphics(GraphicsElement):
    TRACE_COLOR = 100, 100, 255
    DEAD_COLOR = 255, 70, 70
    DEAD_BG_COLOR = 70, 70, 70, 150
    DEAD_X_LINE_1 = [CAR_BOUNDS[0] + 1, CAR_BOUNDS[1] + 2, CAR_BOUNDS[2] - 1, CAR_BOUNDS[3] - 1]
    DEAD_X_LINE_2 = [CAR_BOUNDS[0] + 1, CAR_BOUNDS[3] - 1, CAR_BOUNDS[2] - 1, CAR_BOUNDS[1] + 2]

    def __init__(self, num, level: Level, show_traces=True, show_collision_box=False):
        super().__init__()
        self.tracer = TracerLines(level) if show_traces else None
        self.car_frame = pyglet.sprite.Sprite(img=car_frame_img, batch=self.batch)
        self.car_frame.scale = 0.5

        color_data = 'c3B', random_color() + random_color() + random_color() + random_color()
        pts, vertices, _ = convert_data(CAR_BOUND_POINTS)
        self.car_color = pyglet.graphics.vertex_list(pts, vertices, color_data)
        car_text = pyglet.text.decode_text(str(num))
        car_num_col = (255, 255, 255, 255) if np.average(color_data[1]) <= 127 else (0, 0, 0, 255)
        car_text.set_style(0, len(car_text.text), dict(font_name='Arial', font_size=8, color=car_num_col))
        self.car_num = pyglet.text.layout.TextLayout(car_text, width=30)
        self.car_num.x, self.car_num.y = -4, -2

        self.dead_x = [create_vertex_list(CAR_BOUND_POINTS, self.DEAD_BG_COLOR, color_mode='c4B'),
                       create_vertex_list(self.DEAD_X_LINE_1, self.DEAD_COLOR),
                       create_vertex_list(self.DEAD_X_LINE_2, self.DEAD_COLOR)]
        self.show_dead_x = False
        self.collision_box = create_vertex_list(CAR_BOUND_POINTS, self.DEAD_COLOR, vertices_mode='v2f') \
            if show_collision_box else None

    def draw(self):
        if self.tracer:
            self.__draw_traces()

        self.__draw_at_car_position(self.__draw_car_frame)
        self.batch.draw()
        if self.collision_box:
            self.collision_box.draw(pyglet.gl.GL_POLYGON)
        if self.show_dead_x:
            self.__draw_at_car_position(self.__draw_dead_x)

    def __draw_car_frame(self):
        self.car_color.draw(pyglet.gl.GL_POLYGON)
        pyglet.gl.glRotatef(-90, 0, 0, 1.0)
        self.car_num.draw()

    def __draw_traces(self):
        pyglet.gl.glLineWidth(1)
        for pos in self.tracer.get_trace_points(self.car_frame.position, self.car_frame.rotation):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINE_STRIP,
                                 ('v2f', self.car_frame.position + pos),
                                 ('c3B', self.TRACE_COLOR * 2)
                                 )

    def __draw_dead_x(self):
        pyglet.gl.glLineWidth(5)
        [box, line_1, line_2] = self.dead_x
        line_1.draw(pyglet.gl.GL_LINE_STRIP)
        line_2.draw(pyglet.gl.GL_LINE_STRIP)
        box.draw(pyglet.gl.GL_POLYGON)

    def __draw_at_car_position(self, draw_callback):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.car_frame.x, self.car_frame.y, 0)
        pyglet.gl.glRotatef(-self.car_frame.rotation, 0, 0, 1.0)
        draw_callback()
        pyglet.gl.glPopMatrix()

    def update(self, player: PlayerState):
        self.car_frame.update(x=player.x, y=player.y, rotation=player.rotation)
        self.show_dead_x = not player.is_alive
        if self.collision_box:
            self.collision_box.vertices = player.flattened_boundaries()


class TrackGraphics(GraphicsElement):
    TRACK_COLOR = 160, 10, 60

    def __init__(self, level: Level):
        super().__init__()
        self.add_points(level.outer_track, self.TRACK_COLOR)
        self.add_points(level.inner_track, self.TRACK_COLOR)

        self.obstacles = []  # keep obstacle-sprite refs to avoid removal
        for obs_pos in level.obstacles:
            sprite = pyglet.sprite.Sprite(x=obs_pos.x, y=obs_pos.y, img=box_img, batch=self.batch)
            sprite.update(scale=0.4, rotation=obs_pos.rot)
            self.obstacles.append(sprite)

    def draw(self):
        pyglet.gl.glLineWidth(5)
        self.batch.draw()


class WarmupSequence:
    def __init__(self, level: Level):
        self.__overlays = [(GameOverlay(level, '3', ''), 1.0),
                           (GameOverlay(level, '2', ''), 1.0),
                           (GameOverlay(level, '1', ''), 1.0),
                           (GameOverlay(level, '', 'GO !!!', '', text_only=True), 0.7)]
        self.__current_ix = -1

    def reset(self):
        self.__current_ix = -1

    def __next__(self):
        self.__current_ix += 1
        return self.__is_current_ix_valid()

    def current_delay(self):
        return self.__overlays[self.__current_ix][1]

    def draw(self):
        if self.__is_current_ix_valid():
            self.__overlays[self.__current_ix][0].draw()

    def shows_last_screen(self):
        return self.__current_ix == len(self.__overlays) - 1

    def __is_current_ix_valid(self):
        return 0 <= self.__current_ix < len(self.__overlays)


class GameOverlay(GraphicsElement):
    REGULAR_COLORS = [(255, 255, 0, 255), (255, 255, 150, 255), (30, 30, 30, 150)]
    TEXT_ONLY_COLORS = [(60, 60, 60, 255), (60, 60, 60, 255), (0, 0, 0, 0)]

    def __init__(self, level: Level, main_txt, support_txt, exit_txt='"Esc" to quit', text_only=False):
        super().__init__()
        colors = self.TEXT_ONLY_COLORS if text_only else self.REGULAR_COLORS
        background = pyglet.graphics.OrderedGroup(0)
        cnt, vertices, transparent = convert_data(
            [0, 0, level.width, 0, level.width, level.height, 0, level.height],
            colors[2], color_mode='c4B')
        self.batch.add(4, pyglet.gl.GL_POLYGON, background, vertices, transparent)

        foreground = pyglet.graphics.OrderedGroup(1)
        main_lbl = pyglet.text.Label(main_txt, batch=self.batch, group=foreground,
                                     color=colors[0], font_size=22, bold=True)
        main_lbl.x = level.width / 2 - main_lbl.content_width / 2
        main_lbl.y = level.height / 2 - main_lbl.content_height / 2
        support_lbl = pyglet.text.Label(support_txt, batch=self.batch, group=foreground,
                                        color=colors[1], font_size=16)
        support_lbl.x = level.width / 2 - support_lbl.content_width / 2
        support_lbl.y = level.height / 2 - main_lbl.content_height - support_lbl.content_height
        exit_lbl = pyglet.text.Label(exit_txt, batch=self.batch, group=foreground,
                                     color=colors[1], font_size=16)
        exit_lbl.x = level.width / 2 - exit_lbl.content_width / 2
        exit_lbl.y = level.height / 2 - main_lbl.content_height - exit_lbl.content_height * 2.3


class ScoreBox(GraphicsElement):
    BG_COLOR = 50, 50, 200
    SCORE_BOX = 150, 40

    def __init__(self, level: Level):
        super().__init__()
        offset = np.array((level.width, level.height)) - self.SCORE_BOX
        box = np.append(offset, offset + self.SCORE_BOX)
        self.center_x = offset[0] + self.SCORE_BOX[0] / 2

        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)
        bg_box = [box[0], box[1], box[2], box[1], box[2], box[3], box[0], box[3], box[0], box[1]]
        self.add_points(bg_box, self.BG_COLOR, pyglet.gl.GL_POLYGON, background)
        self.label = pyglet.text.Label(x=level.width - 100, y=level.height - 25,
                                       batch=self.batch, group=foreground)

    def update_text(self, score_text):
        self.label.text = score_text
        self.label.x = self.center_x - self.label.content_width / 2


class RankingBox(GraphicsElement):
    TEXT_COLOR = 40, 40, 40, 255
    NAMES_WIDTH = 105
    SCORES_WIDTH = 30

    def __init__(self, level: Level):
        super().__init__()
        pos_x, pos_y = level.width - 150, level.height - 70
        self.names = pyglet.text.Label(x=pos_x, y=pos_y,
                                       width=self.NAMES_WIDTH, color=self.TEXT_COLOR, font_size=9,
                                       batch=self.batch, multiline=True)
        self.scores = pyglet.text.Label(x=pos_x + self.NAMES_WIDTH, y=pos_y,
                                        width=self.SCORES_WIDTH, color=self.TEXT_COLOR, font_size=9,
                                        batch=self.batch, multiline=True)

    def update(self, ranking):
        if ranking:
            self.names.text, self.scores.text = ranking


class Indicators(GraphicsElement):
    def __init__(self):
        super().__init__()
        self.inner_pointer = Pointer(self.batch)
        self.inner_score = 0
        self.outer_pointer = Pointer(self.batch)
        self.outer_score = 0
        self.mouse_label = pyglet.text.Label('', font_size=14, batch=self.batch)

    def update_mouse(self, x, y):
        self.mouse_label.text = '{}/{}'.format(x, y)
        self.mouse_label.x = x + 10
        self.mouse_label.y = y + 10

    def update(self, state: PlayerState):
        if state.distance == 0:
            self.inner_score = 0
            self.outer_score = 0

        if state.is_alive:
            inner_delta, outer_delta = state.last_deltas

            delta_score, (px, py) = inner_delta
            self.inner_score += delta_score
            self.inner_pointer.update(px, py, '{:.0f}'.format(self.inner_score))

            delta_score, (px, py) = outer_delta
            self.outer_score += delta_score
            self.outer_pointer.update(px, py, '{:.0f}'.format(self.outer_score))


class Pointer:
    def __init__(self, batch):
        super().__init__()
        self.point = pyglet.sprite.Sprite(img=pointer_img, batch=batch)
        self.label = pyglet.text.Label('', font_size=14, batch=batch)

    def update(self, x, y, text=None):
        if text:
            self.label.text = text
        self.label.x = x + 10
        self.label.y = y + 10
        self.point.update(x=x, y=y)
