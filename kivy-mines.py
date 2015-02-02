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
    flag_image = "assets/flag.png"
    flagged = False

    def __init__(self, hidden, line_index, col_index, image=None, *args, **kwargs):
        super(BoardButton, self).__init__(*args, **kwargs)
        self.hidden = hidden
        self.image = image
        self.line_index = line_index
        self.col_index = col_index

    def clear_flag(self):
        self.flagged = False
        self.clear_widgets()


class KivyMines(ScreenManager):
    board = ListProperty()
    horizontal = NumericProperty()
    vertical = NumericProperty()
    bomb_count = NumericProperty(0)
    found_bombs = NumericProperty(0)

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
            if x1 < mouse_position[0] < x2 and y1 < mouse_position[1] < y2:
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
        if button.hidden == 0:
            button.text = ""
        else:
            button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
        button.background_color = HOVER
        button.disabled = True
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
            if -1 < line < self.horizontal and -1 < col < self.vertical:
                button = \
                    filter(lambda x: x.line_index == line and x.col_index == col, self.current_screen.board.children)[0]
                if int(button.hidden) == 0 and not button.disabled:
                    button.clear_flag()
                    self.disable_buttons(button)
                elif int(button.hidden) > 0:
                    button.clear_flag()
                    button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
                    button.background_color = HOVER
                    button.disabled = True

    def check_complete(self):
        count = len(filter(lambda x: x.flagged and x.hidden == -1, self.current_screen.board.children))
        print count, self.bomb_count

    def board_click(self, *args):
        button = args[0]
        if hasattr(button.last_touch, 'multitouch_sim'):
            if button.flagged:
                button.clear_flag()
                self.found_bombs -= 1
            else:
                img = Image(source=button.flag_image,
                            pos=button.pos,
                            size=button.size)
                button.add_widget(img)
                button.text = ""
                button.flagged = True
                self.found_bombs += 1
        else:
            if button.flagged:
                pass
            elif button.hidden == -1:
                exploded_image = Image(source=button.explode_image,
                                       pos=button.pos,
                                       size=button.size)
                button.add_widget(exploded_image)
                button.background_color = RED
                button.disabled = True
                self.bomb_all()
            elif button.hidden == 0:
                self.disable_buttons(button)
            else:
                button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
                button.background_color = HOVER
                button.disabled = True

        self.check_complete()

    def switch_screen(self, screen):
        self.found_bombs = 0
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
            button = BoardButton(text='',  # "[color=000000]%s - %s(%s)[/color]" % (line_index, col_index, cell),
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