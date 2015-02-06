#:kivy 1.8.0

from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.properties import (NumericProperty, ListProperty, BooleanProperty, StringProperty)

from config import HOVER, NORMAL, RED, COLOR_PALETTE
from mine import Mine


class CustomPopup(Popup):
    def __init__(self, **kwargs):
        super(CustomPopup, self).__init__(**kwargs)
        self.separator_height = 0
        self.title_size = 0
        self.background = ""
        grid = self.children[0]
        grid.padding = (0, 0, 0, 0)

        for ch in grid.children:
            if str(ch).find('Label') != -1:
                grid.remove_widget(ch)

            if str(ch).find('Widget') != -1:
                ch.size = (0, 0)


class CustomLabel(Label):
    pass


class BoardButton(Button):
    explode_image = "assets/mine_explode.png"
    flag_image = "assets/flag.png"
    flagged = False
    pressed = False

    def __init__(self, hidden, line_index, col_index, image=None, **kwargs):
        super(BoardButton, self).__init__(**kwargs)
        self.hidden = hidden
        self.image = image
        self.line_index = line_index
        self.col_index = col_index

    def get_neighbours(self):
        line_index, col_index = self.line_index, self.col_index

        top_left = line_index - 1, col_index - 1
        top = line_index - 1, col_index
        top_right = line_index - 1, col_index + 1

        left = line_index, col_index - 1
        right = line_index, col_index + 1

        bot_left = line_index + 1, col_index - 1
        bot = line_index + 1, col_index
        bot_right = line_index + 1, col_index + 1

        return [top_left, top, top_right,
                left, right,
                bot_left, bot, bot_right]

    def clear_flag(self):
        self.flagged = False
        self.clear_widgets()


class KivyMines(ScreenManager):
    board = ListProperty()
    horizontal = NumericProperty()
    vertical = NumericProperty()
    level = NumericProperty(5)
    bomb_count = NumericProperty(0)
    found_bombs = NumericProperty(0)
    game_on = BooleanProperty(False)
    game_since = StringProperty("0:00:00")
    game_at = None
    popup = None

    def hover(self, *args):
        mouse_position = args[1]
        if self.current == "board_selection":
            obj = self.board_selection
        else:
            obj = self.board_screen.board

        for but in filter(lambda x: not x.pressed, obj.children):
            x1, x2 = but.pos[0], but.pos[0] + but.width
            y1, y2 = but.pos[1], but.pos[1] + but.height
            if x1 < mouse_position[0] < x2 and y1 < mouse_position[1] < y2:
                but.background_color = HOVER
            else:
                but.background_color = NORMAL

    def set_level(self, level):
        self.level = level

    def bomb_all(self):
        board = self.current_screen.board
        for cell in board.children:
            if cell.hidden == -1 and not cell.children:
                explode_image = Image(source=cell.image,
                                      pos=cell.pos,
                                      size=cell.size)
                cell.add_widget(explode_image)
            cell.disabled = True
        self.game_on = False

    def counter(self):
        if self.game_on and self.game_at:
            self.game_since = str(datetime.now() - self.game_at).rsplit(".", 1)[0]
            Clock.schedule_once(lambda dt: self.counter(), .5)

    def disable_buttons(self, button):
        if button.hidden == 0:
            button.text = ""
        else:
            button.text = "[b][color=%s]%s[/color][/b]" % (COLOR_PALETTE[button.hidden], button.hidden)
        button.background_color = HOVER
        button.pressed = True

        positions = button.get_neighbours()

        for line, col in positions:
            if -1 < line < self.horizontal and -1 < col < self.vertical:
                button = \
                    filter(lambda x: x.line_index == line and x.col_index == col, self.current_screen.board.children)[0]
                if int(button.hidden) == 0 and not button.pressed:
                    button.clear_flag()
                    self.disable_buttons(button)
                elif int(button.hidden) > 0:
                    button.clear_flag()
                    button.text = "[b][color=%s]%s[/color][/b]" % (COLOR_PALETTE[button.hidden], button.hidden)
                    button.background_color = HOVER
                    button.pressed = True

    def lock_buttons(self):
        buttons = self.current_screen.board.children
        for but in buttons:
            if not but.pressed:
                self.board_click(but, check=False)
            but.disabled = True

    def check_complete(self):
        count = len(filter(lambda x: x.flagged and x.hidden == -1, self.current_screen.board.children))
        if count == self.bomb_count:
            self.lock_buttons()
            self.game_on = False

            if not self.popup:
                label = CustomLabel(text='[b][color=000000]YOU WON[/color][/b]', font_size=40)
                self.popup = CustomPopup(content=label, title="", size_hint=(None, None), size=(400, 200))
                self.popup.open()

    def board_click(self, *args, **kwargs):
        button = args[0]
        check = kwargs.get('check', True)
        auto = kwargs.get('auto', False)

        if not self.game_on and check:
            self.game_on = True
            self.game_at = datetime.now()
            self.counter()
        if button.pressed and button.hidden > 0:
            positions = button.get_neighbours()
            neighbours = []
            for line, col in positions:
                if -1 < line < self.horizontal and -1 < col < self.vertical:
                    neighbour = \
                        filter(lambda x: x.line_index == line and x.col_index == col,
                               self.current_screen.board.children)[0]
                    neighbours.append(neighbour)
            if len(filter(lambda x: x.flagged, neighbours)) == button.hidden:
                for but in filter(lambda x: not x.flagged and not x.pressed, neighbours):
                    self.board_click(but, auto=True)
        else:
            if hasattr(button.last_touch, 'multitouch_sim') and check and not auto and not button.pressed:
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
                    button.pressed = True
                    self.bomb_all()
                elif button.hidden == 0:
                    self.disable_buttons(button)
                else:
                    button.text = "[b][color=%s]%s[/color][/b]" % (COLOR_PALETTE[button.hidden], button.hidden)
                    button.background_color = HOVER
                    button.pressed = True
        if hasattr(button.last_touch, 'multitouch_sim'):
            button.last_touch.multitouch_sim = False
        if check:
            self.check_complete()

    def switch_screen(self, screen, direction='left'):
        self.popup = None
        self.found_bombs = 0
        self.game_on = False
        self.game_at = None
        self.game_since = "0:00:00"
        self.transition = SlideTransition(direction=direction)
        self.current = screen

    def board_select(self, *args):
        self.horizontal, self.vertical = map(int, args)
        mine = Mine(self.horizontal, self.vertical, self.level)
        self.board = map(int, mine.board.reshape(1, self.horizontal * self.vertical)[0])
        self.bomb_count = len(filter(lambda x: x == -1, self.board))
        self.switch_screen(screen='board_screen')

        self.current_screen.board.clear_widgets()

        index = 0
        for cell in self.board:
            line_index = index / self.vertical
            col_index = index % self.vertical
            button = BoardButton(text='',  # "[color=000000]%s[/color]" % (cell),
                                 hidden=cell,
                                 line_index=line_index,
                                 col_index=col_index,
                                 image="assets/mine_exploded.png" if cell else None)
            button.bind(on_press=self.board_click)
            self.current_screen.board.add_widget(button)
            index += 1


class KivyMinesApp(App):
    def __init__(self, **kwargs):
        super(KivyMinesApp, self).__init__(**kwargs)
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