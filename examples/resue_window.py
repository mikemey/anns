import arcade


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHEAT)
        self.all_shapes = None
        self.all_texts = None

    def start(self):
        self.__create_shapes__()
        self.__create_texts__()
        arcade.run()

    def __create_shapes__(self):
        self.all_shapes = arcade.ShapeElementList()
        bg_rect = arcade.create_rectangle_filled(0, 0, 150, 150, arcade.color.GREEN)
        self.all_shapes.append(bg_rect)

    def __create_texts__(self):
        self.all_texts = arcade.SpriteList()
        # draw_text() fails for second window
        text = arcade.draw_text("Hello World!", 0, 0, arcade.color.BLACK, 20, bold=True)
        self.all_texts.append(text)

    def on_draw(self):
        arcade.start_render()
        self.all_shapes.draw()
        self.all_texts.draw()


if __name__ == "__main__":
    for i in range(200, 500, 100):
        game_window = MyGame(i, i, "Hello World")
        game_window.start()
