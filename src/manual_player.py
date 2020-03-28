import arcade

SCREEN_TITLE = "Box pusher"
SPRITE_SCALING = 0.5
FLOOR_TILE_WIDTH = 50
FTW_HALF = FLOOR_TILE_WIDTH / 2

MOVEMENT_SPEED = 1


class PlayerSprite(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def set_to_field(self, field_position):
        self.center_x = field_position[0] * FLOOR_TILE_WIDTH + FTW_HALF
        self.center_y = field_position[1] * FLOOR_TILE_WIDTH + FTW_HALF


class BoxPusherWindow(arcade.Window):
    def __init__(self, engine, title):
        field_width = FLOOR_TILE_WIDTH * engine.field_size[0]
        field_height = FLOOR_TILE_WIDTH * engine.field_size[1]
        super().__init__(field_width, field_height, title)
        self.engine = engine
        self.sprites = None
        self.floor = None
        self.player_sprite = None

        arcade.set_background_color(arcade.color.WHEAT)

    def setup(self):
        self.__create_floor__()

        self.player_sprite = PlayerSprite("resources/player.png", SPRITE_SCALING)
        self.player_sprite.set_to_field(self.engine.player_pos)

        self.sprites = arcade.SpriteList()
        self.sprites.append(self.player_sprite)

    def __create_floor__(self):
        total_width = self.engine.field_size[0] * FLOOR_TILE_WIDTH
        total_height = self.engine.field_size[1] * FLOOR_TILE_WIDTH

        point_list = []
        color_list = []
        for field_x in range(0, self.engine.field_size[0] + 1):
            x = field_x * FLOOR_TILE_WIDTH
            start = (x, 0)
            end = (x, total_height)
            point_list.append(start)
            point_list.append(end)
            for i in range(2):
                color_list.append(arcade.color.BLACK)
        for field_y in range(0, self.engine.field_size[1] + 1):
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

    def on_update(self, delta_time):
        self.sprites.update()

    def on_key_press(self, key, modifiers):
        print('key_press')
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        print('key_release')
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0


class BoxPusherEngine:
    def __init__(self):
        self.field_size = (8, 6)
        self.player_pos = (0, 4)


def main():
    engine = BoxPusherEngine()
    window = BoxPusherWindow(engine, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
