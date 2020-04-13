import arcade
from arcade import Sprite

from game_engine import Direction

SCREEN_TITLE = "Box pusher"
SPRITE_SCALING = 0.5
FLOOR_TILE_WIDTH = 50
FTW_HALF = FLOOR_TILE_WIDTH / 2

KEY_MAPPING = {
    arcade.key.UP: Direction.UP,
    arcade.key.DOWN: Direction.DOWN,
    arcade.key.LEFT: Direction.LEFT,
    arcade.key.RIGHT: Direction.RIGHT,
}

TEXT_WIDTH = 80
SCORE_PANEL_HEIGHT = 45
SCORE_OFFSET = 10
HELP_TEXT_OFFSET = 25
END_OVERLAY_COLOR = (100, 100, 100, 180)

AUTOMATIC_MOVES_DELAY = 0.7


class GameWindowObserver:
    def next_move(self):
        pass

    def game_done(self, quit_game: bool):
        pass


class FieldSprite(Sprite):
    def set_to_field(self, field):
        new_pos = field_to_position(field)
        self.set_position(new_pos[0], new_pos[1])


def field_to_position(field_position):
    return (
        field_position[0] * FLOOR_TILE_WIDTH + FTW_HALF,
        field_position[1] * FLOOR_TILE_WIDTH + FTW_HALF
    )


def append_sprites(sprites_list, positions, sprite_image):
    for field in positions:
        pos = field_to_position(field)
        sprite = FieldSprite(sprite_image, SPRITE_SCALING)
        sprite.center_x = pos[0]
        sprite.center_y = pos[1]
        sprites_list.append(sprite)


class BoxPusherWindow(arcade.Window):
    def __init__(self, game_observer: GameWindowObserver, interactive=True, disable_text=False):
        super().__init__(title=SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHEAT)
        self.set_location(2, 2)

        self.game_observer = game_observer
        self.is_interactive = interactive
        self.disable_text = disable_text

        self.last_move_secs = 0
        self.should_stop = False
        self.engine = None
        self.field_width = None
        self.field_height = None
        self.floor = None
        self.static_sprites = None
        self.player_sprite = None
        self.box_sprites = None
        self.lost_text = None
        self.won_text = None
        self.state_text = None

    def reset_game(self, engine, state_text):
        self.field_width = FLOOR_TILE_WIDTH * engine.field_size[0]
        self.field_height = FLOOR_TILE_WIDTH * engine.field_size[1]
        self.set_size(self.field_width, self.field_height + SCORE_PANEL_HEIGHT)

        self.last_move_secs = 0
        self.should_stop = False
        self.engine = engine
        self.floor = self.__create_floor__()
        self.static_sprites = self.__create_static_sprites__()
        self.player_sprite = self.__create_player__()
        self.box_sprites = self.__create_box_sprites__()

        self.lost_text = self.__create_text__('LOST')
        self.won_text = self.__create_text__('WON')
        self.state_text = state_text

    @staticmethod
    def start():
        arcade.run()

    def stop(self):
        self.should_stop = True

    def __shutdown__(self):
        self.engine = None
        self.floor = None
        self.static_sprites = None
        self.player_sprite = None
        self.box_sprites = None
        self.lost_text = None
        self.won_text = None

        self.close()

    def __game_not_ready__(self):
        return self.engine is None

    @staticmethod
    def __create_player__():
        return FieldSprite("resources/player.png", SPRITE_SCALING)

    def __create_text__(self, result_msg):
        sprites = arcade.SpriteList(is_static=True)
        if not self.disable_text:
            result_text = arcade.draw_text("{} !".format(result_msg), 0, 0, arcade.color.RED_ORANGE, 20, bold=True)
            result_text.set_position(self.field_width / 2, self.field_height / 2)
            sprites.append(result_text)

            next_text = arcade.draw_text("Press 'n' to continue...", 0, 0, arcade.color.DARK_BLUE_GRAY)
            next_text.set_position(self.field_width / 2, self.field_height / 2 - HELP_TEXT_OFFSET)
            sprites.append(next_text)

            quit_text = arcade.draw_text("Press 'q' to quit...", 0, 0, arcade.color.DARK_BLUE_GRAY)
            quit_text.set_position(self.field_width / 2, self.field_height / 2 - (HELP_TEXT_OFFSET * 2))
            sprites.append(quit_text)
        return sprites

    def __create_static_sprites__(self):
        sprites = arcade.SpriteList(is_static=True)
        goal_sprite = FieldSprite("resources/goal.png", SPRITE_SCALING)
        goal_sprite.set_to_field(self.engine.goal)
        sprites.append(goal_sprite)

        append_sprites(sprites, self.engine.walls, "resources/wall.png")
        return sprites

    def __create_box_sprites__(self):
        boxes = arcade.SpriteList()
        append_sprites(boxes, self.engine.boxes, "resources/box.png")
        return boxes

    def __create_floor__(self):
        point_list = []
        color_list = []
        for field_x in range(self.engine.field_size[0] + 1):
            x = field_x * FLOOR_TILE_WIDTH
            start = (x, 0)
            end = (x, self.field_height)
            point_list.append(start)
            point_list.append(end)
            for i in range(2):
                color_list.append(arcade.color.BLACK)

        for field_y in range(self.engine.field_size[1] + 1):
            y = field_y * FLOOR_TILE_WIDTH
            start = (0, y)
            end = (self.field_width, y)
            point_list.append(start)
            point_list.append(end)
            for i in range(2):
                color_list.append(arcade.color.BLACK)

        lines = arcade.create_lines_with_colors(point_list, color_list)

        grid = arcade.ShapeElementList()
        grid.append(lines)
        return grid

    def __draw_stats__(self):
        if not self.disable_text:
            arcade.draw_text('Score: {}'.format(self.engine.points),
                             SCORE_OFFSET * 2, self.field_height + SCORE_OFFSET,
                             arcade.color.DARK_BROWN, 14, bold=True)
            arcade.draw_text(self.state_text,
                             SCORE_OFFSET * 15, self.field_height + SCORE_OFFSET,
                             arcade.color.DARK_BROWN, 14, bold=False)

    def __draw_overlay__(self):
        arcade.draw_rectangle_filled(self.field_width / 2, self.field_height / 2,
                                     self.field_width, self.field_height, END_OVERLAY_COLOR)

    # def __draw_box_pref_positions__(self):
    #     side = FLOOR_TILE_WIDTH * 0.7
    #     for box_pref in self.engine.box_push_positions:
    #         pref_pos = field_to_position(box_pref)
    #         arcade.draw_rectangle_filled(pref_pos[0], pref_pos[1], side, side, arcade.color.LIGHT_GREEN)
    #     for box_pref in self.engine.box_goal_positions:
    #         pref_pos = field_to_position(box_pref)
    #         arcade.draw_rectangle_filled(pref_pos[0], pref_pos[1], side, side, arcade.color.LIGHT_RED_OCHRE)

    def on_draw(self):
        if self.__game_not_ready__():
            return
        arcade.start_render()

        self.floor.draw()
        self.static_sprites.draw()
        self.box_sprites.draw()
        self.player_sprite.draw()
        self.__draw_stats__()

        if self.engine.game_over():
            self.__draw_overlay__()
            if self.engine.game_lost:
                self.lost_text.draw()
            if self.engine.game_won:
                self.won_text.draw()

    def on_update(self, delta_seconds):
        if self.should_stop:
            self.__shutdown__()

        if self.__game_not_ready__() or self.engine.game_over():
            return

        if not self.is_interactive:
            self.last_move_secs += delta_seconds
            if self.last_move_secs > AUTOMATIC_MOVES_DELAY:
                self.last_move_secs = 0
                self.game_observer.next_move()

        self.player_sprite.set_to_field(self.engine.player)
        for ix, box_field in enumerate(self.engine.boxes):
            self.box_sprites[ix].set_to_field(box_field)
        while len(self.box_sprites) > len(self.engine.boxes):
            self.box_sprites.pop()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.game_observer.game_done(True)
        if self.engine.game_over():
            if key == arcade.key.N:
                self.game_observer.game_done(False)
        elif self.is_interactive:
            player_direction = KEY_MAPPING.get(key)
            if player_direction:
                self.engine.player_move(player_direction)
