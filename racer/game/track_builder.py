import pyglet
from pyglet.window import key

from .racer_engine import PlayerState, PlayerOperation
from .racer_graphics import CarGraphics, TrackGraphics, ScoreBox
from .track_builder_modes import coord_format, EditState, AddPointMode, EditPointsMode, InsertPointMode, AddObstaclesMode
from .tracks import EDIT_LEVEL, TrackPosition

TRACK_COLOR = TrackGraphics.TRACK_COLOR
ACTIVE_TRACK_COLOR = 230, 50, 100
COORDS_COLOR = 100, 100, 100, 255
MODE_TXT_COLOR = 45, 45, 45, 255
NAME_COLOR = TrackGraphics.NAME_COLOR


class TrackBuilderWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(EDIT_LEVEL.width, EDIT_LEVEL.height, caption='Track builder')
        self.set_location(0, 0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.batch = pyglet.graphics.Batch()
        description_lbl = pyglet.text.Label(
            'Quit:\nSwitch mode:\nPrint level:\nSwitch track:\nDrive:\nRotate:', align='right',
            x=EDIT_LEVEL.width - ScoreBox.SCORE_BOX[0], y=EDIT_LEVEL.height - 20, width=80,
            font_size=8, multiline=True, batch=self.batch)
        pyglet.text.Label(
            "Esc\nSpace\np\nEnter\n↑↓← →\na / d",
            x=description_lbl.x + description_lbl.width + 10, y=description_lbl.y, width=100,
            font_size=8, multiline=True, batch=self.batch)
        pyglet.text.Label(
            '[ {} ]'.format(EDIT_LEVEL.name), anchor_x='center',
            x=EDIT_LEVEL.width / 2, y=10, color=NAME_COLOR, font_size=16, batch=self.batch)

        self.state = EditState(EDIT_LEVEL)
        self.modes = [AddPointMode(self.state),
                      EditPointsMode(self.state, self.batch),
                      InsertPointMode(self.state, self.batch),
                      AddObstaclesMode(self.state, self.batch)]
        self.mode_ix = 0
        self.mode_lbl = pyglet.text.Label(x=description_lbl.x, y=description_lbl.y - description_lbl.content_height - 10,
                                          font_size=10, color=MODE_TXT_COLOR, batch=self.batch)
        self.__next_mode()

        self.mouse_coords = CoordinateLabel(self.batch, 'Mouse:',
                                            self.mode_lbl.x, self.mode_lbl.y - self.mode_lbl.content_height - 10)
        self.car = CarAdapter(self.batch, EDIT_LEVEL,
                              self.mouse_coords.x, self.mouse_coords.y - self.mouse_coords.content_height - 10)

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
            print('=' * 80)
            print('outer_track:', self.state.outer_track)
            print('inner_track:', self.state.inner_track)
            print('car        :', TrackPosition(self.car.state.x, self.car.state.y, self.car.state.rotation))
            print('obstacles  :', self.state.obstacles)
            print('=' * 80)
        elif symbol == key.ENTER:
            self.state.switch_track()
        else:
            self.car.on_key_press(symbol)
            self.mode.on_key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.car.on_key_release(symbol)
        self.mode.on_key_release(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mode.on_mouse_press(x, y)
        return True

    def on_mouse_enter(self, x, y):
        self.on_mouse_motion(x, y, 0, 0)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mode.on_mouse_motion(x, y)
        self.mouse_coords.update(x, y)

    def update(self, dt):
        self.car.update(dt)
        self.mode.update()


class CoordinateLabel:
    def __init__(self, batch, title, pos_x, pos_y):
        self.x, self.y = pos_x, pos_y
        pyglet.text.Label(title, x=pos_x, y=pos_y, width=50, font_size=9, batch=batch)
        self.coords = pyglet.text.Label(
            coord_format(0, 0), font_name='Verdana', color=COORDS_COLOR,
            x=pos_x + 50, y=pos_y, width=50, font_size=10, multiline=True, batch=batch)

    @property
    def content_height(self):
        return self.coords.content_height

    def update(self, x, y, rot=None):
        self.coords.text = coord_format(x, y)
        if rot:
            self.coords.text += '\nr={:.0f}'.format(round(rot) % 360)


class CarAdapter:
    def __init__(self, batch, level, label_x, label_y):
        self.car_graphics = CarGraphics(1, level, show_traces=False)
        self.operation = PlayerOperation()
        self.state = PlayerState(level)
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
        self.state.update(dt, self.operation)
        self.car_graphics.update(self.state)
        self.car_lbl.update(self.state.x, self.state.y, self.state.rotation)

    def draw(self):
        self.car_graphics.draw()
