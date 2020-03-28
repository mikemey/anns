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
        field_width = FLOOR_TILE_WIDTH * engine.field_size[0]
        field_height = FLOOR_TILE_WIDTH * engine.field_size[1]
        super().__init__(field_width, field_height, title)
        self.engine = engine
        self.sprites = None
        self.floor = None
        self.player_sprite = None
        self.box_sprites = None

        arcade.set_background_color(arcade.color.WHEAT)

    def setup(self):
        self.__create_floor__()
        self.sprites = arcade.SpriteList()

        goal_sprite = FieldSprite("resources/goal.png", SPRITE_SCALING)
        goal_sprite.set_to_field(self.engine.goal)
        self.sprites.append(goal_sprite)

        self.player_sprite = FieldSprite("resources/player.png", SPRITE_SCALING)
        self.sprites.append(self.player_sprite)

        append_sprites(self.sprites, self.engine.walls, "resources/wall.png")

        self.box_sprites = arcade.SpriteList()
        append_sprites(self.box_sprites, self.engine.boxes, "resources/box.png")

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

        self.floor = arcade.ShapeElementList()
        self.floor.append(lines)

    def on_draw(self):
        arcade.start_render()

        self.floor.draw()
        self.sprites.draw()
        self.box_sprites.draw()

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
    engine = BoxPusherEngine(LEVELS[0])
    window = BoxPusherWindow(engine, SCREEN_TITLE)
    window.set_location(0, 0)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
