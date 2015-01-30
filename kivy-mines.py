from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, WipeTransition
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image

from kivy.properties import (NumericProperty, ListProperty)

from mine import Mine


HOVER = get_color_from_hex('ACACAC')
NORMAL = get_color_from_hex('E2DDD5')
RED = get_color_from_hex('990000')


class BoardButton(Button):
    explode_image = "assets/mine_explode.png"

    def __init__(self, hidden, line_index, col_index, image=None, *args, **kwargs):
        super(BoardButton, self).__init__(*args, **kwargs)
        self.hidden = hidden
        self.image = image
        self.line_index = line_index
        self.col_index = col_index


class KivyMines(ScreenManager):
    board = ListProperty()
    horizontal = NumericProperty()
    vertical = NumericProperty()
    bomb_count = NumericProperty()

    def hover(self, *args):
        mouse_position = args[1]
        if self.current == "board_selection":
            obj = self.board_selection
        else:
            obj = self.board_screen.board

        disabled_area = obj.padding[1]
        for but in filter(lambda x: not x.disabled, obj.children):
            x1, x2 = but.pos[0], but.pos[0] + but.height + disabled_area
            y1, y2 = but.pos[1], but.pos[1] + but.width - disabled_area
            if x1 < mouse_position[0] < x2 and \
                                    y1 < mouse_position[1] < y2:
                but.background_color = HOVER
            else:
                but.background_color = NORMAL

    def bomb_all(self):
        board = self.current_screen.board
        for cell in board.children:
            if cell.hidden == -1 and not cell.children:
                explode_image = Image(source=cell.image,
                                      pos=cell.pos,
                                      size=cell.size)
                cell.add_widget(explode_image)
            cell.disabled = True

    def disable_buttons(self, button):
        button.background_color = HOVER

        line_index, col_index = button.line_index, button.col_index

        top_left = line_index - 1, col_index - 1
        top = line_index - 1, col_index
        top_right = line_index - 1, col_index + 1

        left = line_index, col_index - 1
        right = line_index, col_index + 1

        bot_left = line_index + 1, col_index - 1
        bot = line_index + 1, col_index
        bot_right = line_index + 1, col_index + 1

        positions = [top_left, top, top_right,
                     left, right,
                     bot_left, bot, bot_right]

        for line, col in positions:
            board_index = (line * self.vertical) + col
            button = self.current_screen.board.children[board_index]
            if -1 < line < self.horizontal and -1 < col < self.vertical:
                if int(button.hidden) == 0:
                    self.disable_buttons(button)
                elif int(button.hidden) > 0:
                    button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
                    button.background_color = HOVER


    def board_click(self, *args):
        button = args[0]
        if button.hidden == -1:
            exploded_image = Image(source=button.explode_image,
                                   pos=button.pos,
                                   size=button.size)
            button.add_widget(exploded_image)
            button.background_color = RED
            self.bomb_all()
        elif button.hidden == 0:
            self.disable_buttons(button)
        else:
            button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
            button.background_color = HOVER

        button.disabled = True

    def switch_screen(self, screen):
        self.transition = WipeTransition()
        self.current = screen

    def board_select(self, *args):
        self.horizontal, self.vertical = map(int, args)
        mine = Mine(self.horizontal, self.vertical)
        self.board = map(int, mine.board.reshape(1, self.horizontal * self.vertical)[0])
        self.bomb_count = len(filter(lambda x: x == -1, self.board))
        self.switch_screen(screen='board_screen')

        self.current_screen.board.clear_widgets()

        index = 0
        for cell in self.board:
            line_index = index / self.vertical
            col_index = index % self.vertical
            button = BoardButton(text="[color=000000]%s - %s(%s)[/color]" % (line_index, col_index, cell),
                                 hidden=cell,
                                 line_index=line_index,
                                 col_index=col_index,
                                 image="assets/mine_exploded.png" if cell else None)
            button.bind(on_press=self.board_click)
            self.current_screen.board.add_widget(button)
            index += 1


class KivyMinesApp(App):
    def __init__(self, *args, **kwargs):
        super(KivyMinesApp, self).__init__(*args, **kwargs)
        Builder.load_file('assets/mines.kv')
        self.title = 'Kivy Mines'
        self.icon = 'assets/mine.png'

    def build(self):
        mines = KivyMines()
        Window.bind(mouse_pos=mines.hover)
        return mines


if __name__ == '__main__':
    Window.clearcolor = (get_color_from_hex('F0F0F0'))
    KivyMinesApp().run()