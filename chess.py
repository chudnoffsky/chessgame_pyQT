class KingAttack(Exception):
    pass


WHITE = 1
BLACK = 2


def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row, col):
    # проверка, что row и col лежат внутри шахматной доски
    return 0 <= row < 8 and 0 <= col < 8


def print_board(board):
    print('     +----+----+----+----+----+----+----+----+')
    for row in range(7, -1, -1):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board.cell(row, col), end=' ')
        print('|')
        print('     +----+----+----+----+----+----+----+----+')
    print(end='        ')
    for col in range(8):
        print(col, end='    ')
    print()


class Board:
    # главный класс проекта. функции:
    # - создание и завершение игры
    # - создание классов фигур и их работоспособность
    # - создания взаимодействия между фигурами
    def __init__(self, field=None):
        self.cheaker_stop = False
        self.game = True
        self.color = WHITE
        self.TACKING_PAWN_PASS = None
        if not field:
            self.field = []
            for _ in range(8):
                self.field.append([None] * 8)
            self.field[0] = [
                Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
                King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
            ]
            self.field[1] = [
                Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
                Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
            ]
            self.field[6] = [
                Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
                Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
            ]
            self.field[7] = [
                Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
                King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
            ]
        else:
            self.field = self.convetr_from_strform(field)

    def convetr_to_strform(self, field=None):
        strform = str()
        if not field:
            field = self.field
        for i in field:
            for j in i:
                if j:
                    strform += j.char()
                    strform += str(j.get_color())
                else:
                    strform += '00'
        return strform

    def convetr_from_strform(self, strform):
        field = []
        for _ in range(8):
            field.append([None] * 8)
        k = 0
        for i in range(8):
            for j in range(8):
                if strform[k] == 'R':
                    field[i][j] = Rook(int(strform[k + 1]))
                elif strform[k] == 'N':
                    field[i][j] = Knight(int(strform[k + 1]))
                elif strform[k] == 'B':
                    field[i][j] = Bishop(int(strform[k + 1]))
                elif strform[k] == 'Q':
                    field[i][j] = Queen(int(strform[k + 1]))
                elif strform[k] == 'K':
                    field[i][j] = King(int(strform[k + 1]))
                elif strform[k] == 'P':
                    field[i][j] = Pawn(int(strform[k + 1]))
                k += 2

        return field

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        # возврат строки из двух символов
        piece = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def get_piece(self, row, col):
        # возвращает фигуру и ее цвет
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, row, col, row1, col1):
        # перемещение фигуры из точки A в точку B, если это возможно
        if not self.game:
            return False
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку
        piece = self.field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False

        king_is_under_attack = self.king_is_under_attack()
        if piece.can_move(self, row, col, row1, col1):
            if king_is_under_attack or self.king_will_under_attack_move(row, col, row1, col1):
                if self.antishah(row, col, row1, col1):
                    return self.move_piece_change(row, col, row1, col1, piece)
                else:
                    raise KingAttack('Невозможный ход, так как фигура "Король" будет атакована!')
            else:
                return self.move_piece_change(row, col, row1, col1, piece)
        elif piece.can_attack(self, row, col, row1, col1):
            if king_is_under_attack or self.king_will_under_attack(row, col, row1, col1):
                if self.antishah(row, col, row1, col1):
                    return self.move_piece_change(row, col, row1, col1, piece)
                else:
                    raise KingAttack('Невозможный ход, так как фигура "Король" будет атакована!')
            else:
                return self.move_piece_change(row, col, row1, col1, piece)
        raise Exception('Увы, фигура не может так ходить')

    def move_piece_change(self, row, col, row1, col1, piece):
        self.field[row][col].m += 1
        self.field[row][col] = None
        self.field[row1][col1] = piece
        self.color = opponent(self.color)
        self.is_game_stop()
        return True

    def is_game_stop(self):
        self.cheaker_stop = True
        TACKING_PAWN_PASS = self.TACKING_PAWN_PASS
        step = list()
        for row in range(7, -1, -1):
            for col in range(8):
                piece = self.field[row][col]
                if piece is None:
                    continue
                elif piece.get_color() == self.color:
                    for row1 in range(7, -1, -1):
                        for col1 in range(8):
                            if piece.can_attack(self, row, col, row1, col1):
                                if self.king_is_under_attack() or self.king_will_under_attack(row, col, row1, col1):
                                    if self.antishah(row, col, row1, col1):
                                        step.append(True)
                                    else:
                                        step.append(False)
                                else:
                                    step.append(True)
                            elif piece.can_move(self, row, col, row1, col1):
                                if self.king_is_under_attack() or self.king_will_under_attack_move(row, col, row1,
                                                                                                   col1):
                                    if self.antishah(row, col, row1, col1):
                                        step.append(True)
                                    else:
                                        step.append(False)
                                else:
                                    step.append(True)
                            else:
                                step.append(False)
        self.TACKING_PAWN_PASS = TACKING_PAWN_PASS
        self.cheaker_stop = False
        if True not in step:
            self.game = False
            if self.king_is_under_attack():
                raise KingAttack(f'Игра закончена - Мат.')
            else:
                raise KingAttack(f'Игра закончена - Ничья')
        elif self.king_is_under_attack():
            raise KingAttack(f'Королю шах!')
        set_field = set(self.convetr_to_strform())
        if len(set_field & {'R', 'N', 'B', 'Q', 'K', 'P'}) <= 2:
            if (set_field & {'R', 'N', 'B', 'Q', 'K', 'P'} == {'K' 'N'}) or (
                    set_field & {'R', 'N', 'B', 'Q', 'K', 'P'} == {'K'}):
                self.game = False
                raise KingAttack(f'Игра закончена - Ничья')

    def char(self, row, col):
        return self.cell(row, col)[1]

    def field_color(self, row, col):
        if self.cell(row, col)[0] == 'w':
            color = 1
        elif self.cell(row, col)[0] == 'b':
            color = 2
        else:
            color = 0
        return color

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        if self.char(row, col) == 'P':
            if not correct_coords(row, col) or not correct_coords(row1, col1):
                return False
            if row == row1 and col == col1:
                return False
            piece = self.field[row][col]
            if piece is None:
                return False
            if piece.get_color() != self.color:
                return False
            if self.field[row1][col1] is None:
                if not piece.can_move(self, row, col, row1, col1):
                    return False
            elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
                if not piece.can_attack(self, row, col, row1, col1):
                    return False
            else:
                return False

            if (self.color == 1 and row1 != 7) or (self.color == 2 and row1 != 0):
                return False

            if char == 'Q':
                char = Queen(self.color)
            elif char == 'R':
                char = Rook(self.color)
            elif char == 'N':
                char = Knight(self.color)
            elif char == 'B':
                char = Bishop(self.color)
            else:
                return False

            if row == row1:
                self.field[row][col].m += 1
                self.field[row][col] = None
                self.field[row1][col1] = None
                if self.color == 1:
                    self.field[row1 + 1][col1] = char
                else:
                    self.field[row1 - 1][col1] = char
                self.color = opponent(self.color)
                return True
            else:
                self.field[row][col].m += 1
                self.field[row][col] = None
                self.field[row1][col1] = char
                self.color = opponent(self.color)
                return True
        else:
            return False

    def number_of_moves(self, row, col):
        return self.field[row][col].m

    def for_castling(self, row, col, row1, col1):
        piece = self.field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        if col == 4 and col1 == 6:
            for i in range(4, 7, 1):
                if self.king_will_under_attack_move(row, col, row1, i):
                    return False
        elif col == 4 and col1 == 2:
            for i in range(4, 1, -1):
                if self.king_will_under_attack_move(row, col, row1, i):
                    return False

        king_is_under_attack = self.king_is_under_attack()
        if king_is_under_attack or self.king_will_under_attack_move(row, col, row1, col1):
            if self.antishah(row, col, row1, col1):
                return True
            else:
                return False
        else:
            return True

    def castling0(self, row, col, row1, col1):
        colR = 0
        colK = 4

        if self.color == 1:
            if col != colK or row != 0 or row1 != 0 or col1 != 2:
                return False
            if not self.for_castling(row, col, row1, col1):
                return False
            if self.char(row, colR) == 'R':
                m = self.number_of_moves(row, colR)
                if m != 0:
                    return False
            if self.char(row, colK) == 'K':
                n = self.number_of_moves(row, colK)
                if n != 0:
                    return False
            for c in range(1, 4):
                if not (self.get_piece(row, c) is None):
                    return False
            if self.char(row, colR) == 'R' and self.cell(row, colR)[0] == 'w' \
                    and self.char(row, colK) == 'K' and \
                    self.cell(row, colK)[0] == 'w':
                self.field[row][colR] = None
                self.field[0][3] = Rook(WHITE)
                self.field[row][colK] = None
                self.field[0][2] = King(WHITE)
                self.color = opponent(self.color)
                return True
            else:
                return False
        elif self.color == 2:
            if col != colK or row != 7 or row1 != 7 or col1 != 2:
                return False
            if self.char(row, colR) == 'R':
                m = self.number_of_moves(row, colR)
                if m != 0:
                    return False
            if self.char(row, colK) == 'K':
                n = self.number_of_moves(row, colK)
                if n != 0:
                    return False
            for c in range(1, 4):
                if not (self.get_piece(row, c) is None):
                    return False
            if self.char(row, colR) == 'R' and self.cell(row, colR)[0] == 'b' \
                    and self.char(row, colK) == 'K' and \
                    self.cell(row, colK)[0] == 'b':
                self.field[row][colR] = None
                self.field[7][3] = Rook(BLACK)
                self.field[row][colK] = None
                self.field[7][2] = King(BLACK)
                self.color = opponent(self.color)
                return True
            else:
                return False

    def castling7(self, row, col, row1, col1):
        colR = 7
        colK = 4
        if self.color == 1:
            if col != colK or row != 0 or row1 != 0 or col1 != 6:
                return False
            if not self.for_castling(row, col, row1, col1):
                return False
            if self.char(row, colR) == 'R':
                m = self.number_of_moves(row, colR)
                if m != 0:
                    return False
            if self.char(row, colK) == 'K':
                n = self.number_of_moves(row, colK)
                if n != 0:
                    return False
            for c in range(5, 7):
                if not (self.get_piece(row, c) is None):
                    return False
            if self.char(row, colR) == 'R' and self.cell(row, colR)[0] == 'w' \
                    and self.char(row, colK) == 'K' and \
                    self.cell(row, colK)[0] == 'w':
                self.field[row][colR] = None
                self.field[0][5] = Rook(WHITE)
                self.field[row][colK] = None
                self.field[0][6] = King(WHITE)
                self.color = opponent(self.color)
                return True
            else:
                return False
        elif self.color == 2:
            if col != colK or row != 7 or row1 != 7 or col1 != 6:
                return False
            if self.char(row, colR) == 'R':
                m = self.number_of_moves(row, colR)
                if m != 0:
                    return False
            if self.char(row, colK) == 'K':
                n = self.number_of_moves(row, colK)
                if n != 0:
                    return False
            for c in range(5, 7):
                if not (self.get_piece(row, c) is None):
                    return False
            if self.char(row, colR) == 'R' and self.cell(row, colR)[0] == 'b' \
                    and self.char(row, colK) == 'K' and \
                    self.cell(row, colK)[0] == 'b':
                self.field[row][colR] = None
                self.field[7][5] = Rook(BLACK)
                self.field[row][colK] = None
                self.field[7][6] = King(BLACK)
                self.color = opponent(self.color)
                return True
            else:
                return False

    def is_under_attack(self, row, col):
        for r in range(7, -1, -1):
            for c in range(8):
                if not (self.field[r][c] is None) \
                        and self.field[r][c].color == opponent(self.color) \
                        and self.field[r][c].can_attack(self, r, c, row, col):
                    return True
        return False

    def king_is_under_attack(self):
        for row in range(7, -1, -1):
            for col in range(8):
                if self.char(row, col) == 'K' and self.color == self.field_color(row, col):
                    if self.is_under_attack(row, col):
                        return True
                    else:
                        return False

    def king_will_under_attack_move(self, row, col, row1, col1):
        self.field[row][col].m += 1
        self.field[row][col], self.field[row1][col1] = self.field[row1][col1], self.field[row][col]

        for_r = self.king_is_under_attack()

        self.field[row1][col1].m -= 1
        self.field[row1][col1], self.field[row][col] = self.field[row][col], self.field[row1][col1]

        return for_r

    def king_will_under_attack(self, row, col, row1, col1):
        piece = self.field[row1][col1]

        self.field[row][col].m += 1
        self.field[row][col], self.field[row1][col1] = None, self.field[row][col]

        for_r = self.king_is_under_attack()

        self.field[row1][col1].m -= 1
        self.field[row][col], self.field[row1][col1] = self.field[row1][col1], piece

        return for_r

    def antishah(self, row, col, row1, col1):
        return not self.king_will_under_attack(row, col, row1, col1)


class Rook:
    # ладья
    def __init__(self, color):
        self.color = color
        self.m = 0

    def get_color(self):
        return self.color

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        if row1 > row:
            stepr = 1
        elif row1 < row:
            stepr = -1
        else:
            stepr = 0

        if col1 > col:
            stepc = 1
        elif col1 < col:
            stepc = -1
        else:
            stepc = 0

        r = row
        c = col
        if stepr != 0 and stepc == 0:
            for _ in range(row, row1, stepr):
                r += stepr
                c += stepc
                # если на пути по вертикали есть фигура
                if not (board.get_piece(r - stepr, c) is None) and \
                        board.cell(r - stepr, c)[0] != board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if stepr == 0 and stepc != 0:
            for _ in range(col, col1, stepc):
                r += stepr
                c += stepc
                # если на пути по горизонтали есть фигура
                if not (board.get_piece(r, c - stepc) is None) and \
                        board.cell(r, c - stepc)[0] != board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if row == row1 or col == col1 and (0 <= row <= 7) and (0 <= col <= 7):
            if row == row1 and col == col1:
                return False
            else:
                return True
        else:
            return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Pawn:
    # пешка
    def __init__(self, color):
        self.color = color
        self.m = 0

    def get_color(self):
        return self.color

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        if col != col1:
            return False

        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # ход на 1 клетку
        if row + direction == row1 and not board.get_piece(row1, col1):
            board.TACKING_PAWN_PASS = None
            return True

        # ход на 2 клетки из начального положения
        if (row == start_row
                and row + 2 * direction == row1
                and not board.get_piece(row1, col1)):
            board.TACKING_PAWN_PASS = [row1, col1]
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if self.color == WHITE else -1
        if row + direction == row1 and (col + 1 == col1 or col - 1 == col1):
            if board.cell(row1, col1)[0] != board.cell(row, col)[0] and not (board.get_piece(row1, col1) is None):
                board.TACKING_PAWN_PASS = None
                return True
            if (board.get_piece(row1, col1) is None
                    and not (board.get_piece(row, col1) is None)
                    and board.char(row, col1) == 'P'
                    and board.cell(row, col1)[0] != board.cell(row, col)[0]):
                if board.field[row][col1] and [row, col1] == board.TACKING_PAWN_PASS:
                    if not board.cheaker_stop:
                        board.field[row][col1] = None
                        board.TACKING_PAWN_PASS = None
                    return True


class Knight:
    # конь
    def __init__(self, color):
        self.m = 0
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'N'

    def can_move(self, board, row, col, row1, col1):
        stepr = row1 - row
        stepc = col1 - col

        if not (board.get_piece(row1, col1) is None) and \
                board.cell(row1, col1)[0] == board.cell(row, col)[0]:
            return False

        if ((((stepr == 1 or stepr == -1) and (stepc == 2 or stepc == -2)) or (
                (stepr == 2 or stepr == -2) and (stepc == 1 or stepc == -1)))
            or row == row1 or col == col1) and (
                0 <= row <= 7) and (0 <= col <= 7):
            if row == row1 or col == col1:
                return False
            else:
                return True
        else:
            return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class King:
    # король
    def __init__(self, color):
        self.color = color
        self.m = 0

    def get_color(self):
        return self.color

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        stepr = row1 - row
        stepc = col1 - col
        if not (board.get_piece(row1, col1) is None) and \
                board.cell(row1, col1)[0] == board.cell(row, col)[0]:
            return False

        if ((stepr == 1 or stepr == -1 or stepr == 0) and
            (stepc == 1 or stepc == -1 or stepc == 0)) and (
                0 <= row <= 7) and (0 <= col <= 7):
            if row == row1 and col == col1:
                return False
            if board.is_under_attack(row1, col1):
                return False
            return True
        else:
            return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Queen:
    # ферзь
    def __init__(self, color):
        self.m = 0
        self.color = color

    def get_color(self):
        return self.color

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):

        if row1 > row:
            stepr = 1
        elif row1 < row:
            stepr = -1
        else:
            stepr = 0

        if col1 > col:
            stepc = 1
        elif col1 < col:
            stepc = -1
        else:
            stepc = 0

        r = row
        c = col
        if stepr != 0 and stepc == 0:
            for _ in range(row, row1, stepr):
                r += stepr
                c += stepc
                # в случае, если на пути по вертикали есть фигура
                if not (board.get_piece(r - stepr, c) is None) and \
                        board.cell(r - stepr, c)[0] != board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if stepr == 0 and stepc != 0:
            for _ in range(col, col1, stepc):
                r += stepr
                c += stepc
                # в случае, если на пути по горизонтали есть фигура
                if not (board.get_piece(r, c - stepc) is None) and \
                        board.cell(r, c - stepc)[0] != board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if stepr != 0 and stepc != 0:
            for _ in range(row, row1, stepr):
                r += stepr
                c += stepc
                if not (board.get_piece(r - stepr, c - stepc) is None) and \
                        board.cell(r - stepr, c - stepc)[0] != \
                        board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if ((row - row1 == col - col1) or (row - row1 == -(col - col1))
            or (row == row1) or (col == col1)) and (
                0 <= row <= 7) and (0 <= col <= 7):
            if row == row1 and col == col1:
                return False
            else:
                return True
        else:
            return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Bishop:
    # слон
    def __init__(self, color):
        self.color = color
        self.m = 0

    def get_color(self):
        return self.color

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        stepc = 1 if (col1 > col) else -1
        stepr = 1 if (row1 > row) else -1
        r = row
        c = col
        if stepr != 0 and stepc != 0:
            for cr in range(col, col1, stepc):
                r += stepr
                c += stepc
                if not (board.get_piece(r - stepr, c - stepc) is None) and \
                        board.cell(r - stepr, c - stepc)[0] != \
                        board.cell(row, col)[0]:
                    return False
                if not (board.get_piece(r, c) is None) and \
                        board.cell(r, c)[0] == board.cell(row, col)[0]:
                    return False

        if ((row - row1 == col - col1) or (row - row1 == -(col - col1))) \
                or (row == row1) or (col == col1) and (
                0 <= row <= 7) and (0 <= col <= 7):
            if row == row1 or col == col1:
                return False
            else:
                return True
        else:
            return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)
