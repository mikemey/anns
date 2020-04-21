import math

import numpy as np
import pyglet
from pyglet.window import key

from .racer_engine import RacerEngine, PlayerOperation
from .racer_graphics import CarGraphics, pointer_img
from .tracks import default_level

TRACK_COLOR = 160, 10, 60
ACTIVE_TRACK_COLOR = 230, 50, 100
COORDS_COLOR = 100, 100, 100, 255
MODE_COLOR = 45, 45, 45, 255


class TrackBuilderWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(default_level.width, default_level.height, caption='Track builder')
        self.set_location(0, 0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.batch = pyglet.graphics.Batch()
        self.description_lbl = pyglet.text.Label(
            'Quit:\nSwitch mode:\nPrint level:\nSwitch track:\nDrive:', align='right',
            x=870, y=685, width=80, font_size=8, multiline=True, batch=self.batch)
        self.keys_lbl = pyglet.text.Label(
            "Esc\nSpace\np\nEnter\n↑↓← →",
            x=960, y=685, width=100, font_size=8, multiline=True, batch=self.batch)

        self.state = EditState()
        self.modes = [AddPointMode(self.state),
                      EditPointsMode(self.state, self.batch),
                      InsertPointMode(self.state, self.batch)]
        self.mode_ix = -1
        self.mode_lbl = pyglet.text.Label(x=890, y=615, font_size=10, color=MODE_COLOR, batch=self.batch)
        self.__next_mode()

        self.mouse_coords = CoordinateLabel(self.batch, 'Mouse:', 890, 590)
        self.car = CarAdapter(self.batch, 890, 550)

    @property
    def mode(self):
        return self.modes[self.mode_ix]

    def __next_mode(self):
        if self.mode_ix >= 0:
            self.mode.set_visible(False)
        self.mode_ix = (self.mode_ix + 1) % len(self.modes)
        self.mode.set_visible(True)
        self.mode_lbl.text = 'mode:  ' + self.mode.name()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.car.draw()
        self.mode.draw()
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol == key.SPACE:
            self.__next_mode()
        elif symbol == key.P:
            print('Outer track:')
            print(self.state.all_tracks[0])
            print('Inner track:')
            print((self.state.all_tracks[1]))
        elif symbol == key.ENTER:
            self.mode.switch_track()
        else:
            self.car.on_key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.car.on_key_release(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mode.mouse_press(x, y)
        return True

    def on_mouse_enter(self, x, y):
        self.on_mouse_motion(x, y, 0, 0)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mode.mouse_motion(x, y)
        self.mouse_coords.update(x, y)

    def update(self, dt):
        self.car.update(dt)
        self.mode.update()


class EditState:
    def __init__(self):
        self.all_tracks = (default_level.outer_track, default_level.inner_track)
        self.track_ix = 0
        self.track = self.all_tracks[self.track_ix]
        self.mouse = [0, 0]

    def coords(self, ix):
        return self.track[ix], self.track[ix + 1]


class EditMode:
    def __init__(self, state: EditState):
        self.state = state

    def name(self):
        raise NotImplementedError()

    def set_visible(self, visible):
        pass

    def switch_track(self):
        self.state.track_ix = 0 if self.state.track_ix == 1 else 1
        self.state.track = self.state.all_tracks[self.state.track_ix]

    def mouse_motion(self, x, y):
        self.state.mouse = [x, y]

    def mouse_press(self, x, y):
        pass

    def draw(self):
        self.__draw_track(0)
        self.__draw_track(1)

    def __draw_track(self, track_ix):
        pts = self.get_track_points(track_ix)
        pt_count = int(len(pts) / 2)
        color = ACTIVE_TRACK_COLOR if self.state.track_ix == track_ix else TRACK_COLOR
        line_width = 5 if self.state.track_ix == track_ix else 3
        pyglet.gl.glLineWidth(line_width)
        pyglet.graphics.draw(pt_count, pyglet.gl.GL_LINE_STRIP,
                             ('v2i', pts), ('c3B', color * pt_count)
                             )

    def get_track_points(self, track_ix):
        return self.state.all_tracks[track_ix]

    def closest_track_point_ix_to_mouse(self):
        mouse = np.array(self.state.mouse)
        min_distance = math.inf
        closest_ix = -1
        for ix in range(0, len(self.state.track), 2):
            track_pt = (self.state.track[ix], self.state.track[ix + 1])
            dist = np.linalg.norm(mouse - track_pt)
            if dist < min_distance:
                min_distance = dist
                closest_ix = ix
        return closest_ix

    def update(self):
        pass


class AddPointMode(EditMode):
    def __init__(self, state):
        super().__init__(state)

    def name(self):
        return 'ADD'

    def mouse_press(self, x, y):
        self.state.track += [x, y]

    def get_track_points(self, track_ix):
        pts = self.state.all_tracks[track_ix].copy()
        if self.state.track_ix == track_ix:
            pts.extend(self.state.mouse)
        return pts


class EditPointsMode(EditMode):
    def __init__(self, state, batch):
        super().__init__(state)
        self.track_point = TrackPoint(batch=batch)
        self.set_visible(False)
        self.select_point_ix = -1

    def name(self):
        return 'EDIT'

    def set_visible(self, visible):
        self.track_point.set_visible(visible)

    def mouse_press(self, x, y):
        self.select_point_ix = -1 if self.select_point_ix >= 0 \
            else self.closest_track_point_ix_to_mouse()

    def mouse_motion(self, x, y):
        super().mouse_motion(x, y)
        if self.select_point_ix >= 0:
            self.state.track[self.select_point_ix] = x
            self.state.track[self.select_point_ix + 1] = y

    def update(self):
        px, py = self.state.coords(self.closest_track_point_ix_to_mouse())
        self.track_point.update(px, py)


class InsertPointMode(EditMode):
    def __init__(self, state, batch):
        super().__init__(state)
        self.track_points = [TrackPoint(batch=batch, show_xy=False), TrackPoint(batch=batch, show_xy=False)]
        self.set_visible(False)
        self.insert_ix = -1

    def name(self):
        return 'INSERT'

    def set_visible(self, visible):
        for pt in self.track_points:
            pt.set_visible(visible)

    def mouse_press(self, x, y):
        self.insert_ix = -1 if self.insert_ix >= 0 \
            else self.closest_track_point_ix_to_mouse() + 2

        if self.insert_ix >= 0:
            self.set_visible(False)
            self.state.track.insert(self.insert_ix, self.state.mouse[1])
            self.state.track.insert(self.insert_ix, self.state.mouse[0])
        else:
            self.set_visible(True)

    def mouse_motion(self, x, y):
        super().mouse_motion(x, y)
        if self.insert_ix >= 0:
            self.state.track[self.insert_ix] = x
            self.state.track[self.insert_ix + 1] = y

    def update(self):
        ix = self.closest_track_point_ix_to_mouse()
        self.track_points[0].update(*self.state.coords(ix))

        second_ix = ix + 2
        if second_ix >= len(self.state.track):
            second_ix = ix - 2
        self.track_points[1].update(*self.state.coords(second_ix))


class TrackPoint:
    def __init__(self, batch, font_size=8, offset=15, show_xy=True):
        super().__init__()
        self.point = pyglet.sprite.Sprite(img=pointer_img, batch=batch)
        self.label = pyglet.text.Label('', font_size=font_size, batch=batch, font_name='Verdana',
                                       color=COORDS_COLOR, multiline=True, width=50) \
            if show_xy else None
        self.offset = offset

    def set_visible(self, visible):
        self.point.visible = visible
        if self.label:
            self.label.text = ''

    def update(self, x, y):
        self.point.update(x=x, y=y)
        if self.label:
            self.label.x = x + self.offset
            self.label.y = y + self.offset / 2
            self.label.text = coord_format(x, y)


class CoordinateLabel:
    def __init__(self, batch, title, pos_x, pos_y):
        pyglet.text.Label(title, x=pos_x, y=pos_y, width=50, font_size=9, batch=batch)
        self.coords = pyglet.text.Label(
            coord_format(0, 0), font_name='Verdana', color=COORDS_COLOR,
            x=pos_x + 50, y=pos_y, width=50, font_size=10, multiline=True, batch=batch)

    def update(self, x, y, rot=None):
        self.coords.text = coord_format(x, y)
        if rot:
            self.coords.text += '\nr={:.0f}'.format(rot)


def coord_format(x, y):
    return 'x={:.0f}\ny={:.0f}'.format(x, y)


class CarAdapter:
    def __init__(self, batch, label_x, label_y):
        self.car_graphics = CarGraphics(1, default_level, show_traces=False)
        self.operation = PlayerOperation()
        self.engine = RacerEngine(default_level)
        self.car_lbl = CoordinateLabel(batch, 'Car:', label_x, label_y)

    def on_key_press(self, symbol):
        if symbol == key.UP:
            self.operation.accelerate()
        if symbol == key.DOWN:
            self.operation.reverse()
        if symbol == key.LEFT:
            self.operation.turn_left()
        if symbol == key.RIGHT:
            self.operation.turn_right()

    def on_key_release(self, symbol):
        if symbol in (key.UP, key.DOWN):
            self.operation.stop_direction()
        if symbol == key.LEFT:
            self.operation.stop_left()
        if symbol == key.RIGHT:
            self.operation.stop_right()

    def update(self, dt):
        self.car_graphics.update(self.engine.player_state)
        self.engine.update(dt, self.operation)
        self.car_lbl.update(self.engine.player_state.x, self.engine.player_state.y, self.engine.player_state.rotation)

    def draw(self):
        self.car_graphics.draw()
