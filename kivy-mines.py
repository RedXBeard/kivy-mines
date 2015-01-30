from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, WipeTransition
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image

from kivy.properties import (NumericProperty, ListProperty)

from mine import Mine


class BoardButton(Button):
    explode_image = "assets/mine_explode.png"
    def __init__(self, hidden, image=None, *args, **kwargs):
        super(BoardButton, self).__init__(*args, **kwargs)
        self.hidden = hidden
        self.image = image


class KivyMines(ScreenManager):
    board = ListProperty()
    horizontal = NumericProperty()
    vertical = NumericProperty()

    def hover(self, *args):
        hover = get_color_from_hex('ACACAC')
        normal = get_color_from_hex('E2DDD5')

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
                but.background_color = hover
            else:
                but.background_color = normal
                # print but.text, x1, x2, '-', y1, y2
                # print mouse_position
                # print ""

    def bomb_all(self):
        board = self.current_screen.board
        for cell in board.children:
            if cell.hidden == -1 and not cell.children:
                explode_image = Image(source=cell.image,
                                      pos=cell.pos,
                                      size=cell.size)
                cell.add_widget(explode_image)
            cell.disabled = True

    def board_click(self, *args):
        button = args[0]
        if button.hidden == -1:
            exploded_image = Image(source=button.explode_image,
                                   pos=button.pos,
                                   size=button.size)
            button.add_widget(exploded_image)
            self.bomb_all()
        elif button.hidden == 0:
            button.text = ""
        else:
            button.text = "[color=009900][size=45]%s[/size][/color]" % button.hidden
        button.disabled = True

    def switch_screen(self, screen):
        self.transition = WipeTransition()
        self.current = screen

    def board_select(self, *args):
        self.horizontal, self.vertical = map(int, args)
        mine = Mine(self.horizontal, self.vertical)
        self.board = map(int, mine.board.reshape(1, self.horizontal * self.vertical)[0])
        self.switch_screen(screen='board_screen')

        self.current_screen.board.clear_widgets()
        for cell in self.board:
            button = BoardButton(text="[color=000000]%s[/color]" % cell,
                                 hidden=cell,
                                 image="assets/mine_exploded.png" if cell else None)
            button.bind(on_press=self.board_click)
            self.current_screen.board.add_widget(button)


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