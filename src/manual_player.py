import arcade
from arcade import Sprite
from game_engine import BoxPusherEngine, Direction
from levels import LEVELS

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


class FieldSprite(Sprite):
    def set_to_field(self, field):
        new_pos = field_to_position(field)
        self.center_x = new_pos[0]
        self.center_y = new_pos[1]


class BoxPusherWindow(arcade.Window):
    def __init__(self, engine, title):
        self.field_width = FLOOR_TILE_WIDTH * engine.field_size[0]
        self.field_height = FLOOR_TILE_WIDTH * engine.field_size[1]
        super().__init__(self.field_width, self.field_height + SCORE_PANEL_HEIGHT, title)
        self.engine = engine
        self.floor = self.__create_floor__()
        self.sprites = self.__create_sprites__()
        self.player_sprite = self.__create_player__()
        self.sprites.append(self.player_sprite)
        self.box_sprites = self.__create_box_sprites__()

        self.lost_screen = self.__create_screen__('LOST')
        self.won_screen = self.__create_screen__('WON')
        arcade.set_background_color(arcade.color.WHEAT)

    @staticmethod
    def __create_player__():
        return FieldSprite("resources/player.png", SPRITE_SCALING)

    def __create_screen__(self, result_msg):
        overlay_color = (100, 100, 100, 180)
        overlay = arcade.create_rectangle_filled(self.field_width / 2, self.field_height / 2,
                                                 self.field_width, self.field_height, overlay_color)

        text = arcade.draw_text("{} !".format(result_msg), 0, 0, arcade.color.RED_ORANGE, 20, bold=True)
        text.set_position(self.field_width / 2, self.field_height / 2)
        return overlay, text

    def __create_sprites__(self):
        sprites = arcade.SpriteList()
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
        total_width = self.engine.field_size[0] * FLOOR_TILE_WIDTH
        total_height = self.engine.field_size[1] * FLOOR_TILE_WIDTH

        point_list = []
        color_list = []
        for field_x in range(self.engine.field_size[0] + 1):
            x = field_x * FLOOR_TILE_WIDTH
            start = (x, 0)
            end = (x, total_height)
            point_list.append(start)
            point_list.append(end)
            for i in range(2):
                color_list.append(arcade.color.BLACK)
        for field_y in range(self.engine.field_size[1] + 1):
            y = field_y * FLOOR_TILE_WIDTH
            start = (0, y)
            end = (total_width, y)
            point_list.append(start)
            point_list.append(end)
            for i in range(2):
                color_list.append(arcade.color.BLACK)

        lines = arcade.create_lines_with_colors(point_list, color_list)

        grid = arcade.ShapeElementList()
        grid.append(lines)
        return grid

    def on_draw(self):
        arcade.start_render()

        self.floor.draw()
        self.sprites.draw()
        self.box_sprites.draw()

        arcade.draw_text('Score: {}'.format(self.engine.points),
                         SCORE_OFFSET * 2, self.field_height + SCORE_OFFSET,
                         arcade.color.DARK_BROWN, 14, bold=True)
        if self.engine.game_lost:
            for el in self.lost_screen:
                el.draw()
        if self.engine.game_won:
            for el in self.won_screen:
                el.draw()

    def on_update(self, delta_time):
        self.player_sprite.set_to_field(self.engine.player)

        for ix, box_field in enumerate(self.engine.boxes):
            self.box_sprites[ix].set_to_field(box_field)
        while len(self.box_sprites) > len(self.engine.boxes):
            self.box_sprites.pop()

    def on_key_press(self, key, modifiers):
        player_direction = KEY_MAPPING.get(key)
        if player_direction:
            self.engine.player_move(player_direction)


def main():
    engine = BoxPusherEngine(LEVELS[1])
    window = BoxPusherWindow(engine, SCREEN_TITLE)
    window.set_location(0, 0)
    arcade.run()


if __name__ == "__main__":
    main()
