from random import randint

from numpy import zeros


class Mine(object):
    def __init__(self, horizontal=16, vertical=16):
        self.horizontal = horizontal
        self.vertical = vertical
        self.board = zeros(self.horizontal * self.vertical)
        self.bomb_count = self.horizontal * self.vertical / 5
        # Prepare the Board.
        self.locate_bombs()
        self.reshape_board()
        self.point_neighbours()

    def as_str(self):
        """
        To see the board view on terminal or any other viewable screen
        """
        ss = ""
        for line in self.board:
            ss += "\t".join(map(str, map(int, line))) + "\n\v"
        return ss

    def locate_bombs(self):
        """
        Randomly find bomb positions on board bomb count calculated at the beginning
        positions signed with the value of random index with '-1'
        if the count of these signed positions are reached the calculated bomb count,
        iterations will be stopped. The key point is, with little posibility,
        same index should be passed by this way this problem will be eliminated.
        """
        while len(filter(lambda x: x == -1, self.board)) < self.bomb_count:
            i = randint(0, (self.horizontal * self.vertical) - 1)
            self.board[i] = -1

    def reshape_board(self):
        """
        Board should be shaped with wanted horizontal and vertical count.
        """
        self.board = self.board.reshape(self.horizontal, self.vertical)

    def point_neighbours(self):
        """
        Neighbours bomb count will be calculated.
        """
        line_index = 0
        for line in self.board:
            col_index = 0
            for col in line:
                if col == -1:
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

                    for line_pos, col_pos in positions:
                        try:
                            if -1 < line_pos < self.horizontal and \
                                                    -1 < col_pos < self.vertical and \
                                            self.board[line_pos][col_pos] > -1:
                                self.board[line_pos][col_pos] += 1
                        except IndexError:
                            pass

                col_index += 1
            line_index += 1
        pass
