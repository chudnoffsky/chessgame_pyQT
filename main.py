from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QDesktopWidget, QInputDialog, QMessageBox
from Viewing import Ui_Dialog
from os import remove
import chess
import csv
import sqlite3
import sys


class ChessBoard(Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.boards_list = []
        self.steps_list = []
        self.initUI()
        self.chess_choice.clicked.connect(self.chess_start)
        self.exit_bt.clicked.connect(self.good_bye)
        self.game_choice.clicked.connect(self.viewing_games)
        self.status = "menu"
        self.sql_base = sqlite3.connect("data.db")
        self.table_btn1.clicked.connect(self.change_board)
        self.table_btn2.clicked.connect(self.change_board)
        self.name = None

    def update_bord(self, start=False, capt='', appending=True):
        if start:
            for i in range(8, 0, -1):
                self.findChild(QLabel, f'{i}').setVisible(True)
            for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                self.findChild(QLabel, f'{i}').setVisible(True)

        for row in range(7, -1, -1):
            for col in range(8):
                if start:
                    self.findChild(QPushButton, f'{row}{col}').setVisible(True)
                figure = str(self.board.cell(row, col))
                style = self.figure_style(figure, [row, col])
                self.findChild(QPushButton, f'{row}{col}').setStyleSheet(style)
                if start:
                    self.findChild(QPushButton, f'{row}{col}').clicked.connect(self.game_chess)
        if appending:
            self.caption_about_game(capt)
            if self.board.convetr_to_strform() != chess.Board().convetr_to_strform():
                self.boards_list.append(self.board.convetr_to_strform())
            try:
                k = str(((len(self.steps_list) - 1) // 2) + 1) + '.' + str(abs((len(self.steps_list) % 2) - 2))
                if "шах" in capt:
                    self.steps_list[-1] += "+"
                elif "Мат" in capt:
                    self.steps_list[-1] += "#"
                self.table.addItem(k + ') ' + self.steps_list[-1])
            except:
                pass

    def remember_item(self, item):
        if self.status == "viewing_game" and item:
            self.name = item.text()
            i = self.name[:self.name.find(')'):]
            i = list(map(int, i.split('.')))
            i = (i[0] * 2 - abs(2 - i[1])) - 1
            self.board = chess.Board(self.boards_list[i])
            self.update_bord(False, '', False)
        else:
            self.name = item.text()

    def change_board(self, item):
        if item:
            self.remember_item(item)
        try:
            text = self.sender().text()
        except:
            text = 1

        if self.status == "viewing_games" and text == "Удалить" and self.name:
            con = self.sql_base
            cur = con.cursor()
            cur.execute("""DELETE from Games
                           WHERE play_name = '{}'""".format(self.name))
            con.commit()
            print(f'chess_game/{self.name}.csv')
            remove(f'chess_game/{self.name}.csv')
            self.table.clear()
            for i in cur.execute("""SELECT play_name FROM Games""").fetchall():
                self.table.addItem(i[0])
        elif self.status == "chess" and self.board.game:
            if 1 == self.board.color:
                self.steps_list.append('Белые сдались')
                self.findChild(QLabel, 'label_caption').setText('♞ Белые сдались')
            else:
                self.steps_list.append('Черные сдались')
                self.findChild(QLabel, 'label_caption').setText('♘ Черные сдались')
            self.boards_list.append(self.board.convetr_to_strform())
            self.board.game = False
            self.end_game()
        elif self.status == "viewing_games" and self.name:
            self.status = "viewing_game"
            self.table_btn1.setVisible(False)
            self.table_btn2.setText('Назад')
            self.table.clear()
            csvfile = open(f'chess_game/{self.name}.csv', encoding="utf8")
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                if row:
                    self.steps_list.append(row[0])
                    self.boards_list.append(row[1])
            csvfile.close()
            for i in range(len(self.steps_list)):
                k = str((i // 2) + 1) + '.' + str(abs((i % 2) + 1))
                self.table.addItem(k + ') ' + self.steps_list[i])
            self.name = None
        elif self.status == "viewing_game" and text != 1:
            self.table_btn2.setText('Удалить')
            self.status = "viewing_games"
            self.table_btn1.setVisible(True)
            self.table.clear()
            for i in self.sql_base.cursor().execute("""SELECT play_name FROM Games""").fetchall():
                self.table.addItem(i[0])

    def viewing_games(self):
        # отображение меню
        self.exit_bt.setText('Главное меню')
        self.table_btn1.setVisible(True)
        self.table_btn2.setVisible(True)
        self.table.itemClicked.connect(self.remember_item)
        self.table.itemActivated.connect(self.change_board)
        self.boards_list = list()
        self.steps_list = list()
        self.status = 'viewing_games'
        self.board.game = False
        self.table.setVisible(True)
        con = self.sql_base
        cur = con.cursor()
        for i in cur.execute("""SELECT play_name FROM Games""").fetchall():
            self.table.addItem(i[0])
        self.chess_choice.setVisible(False)
        self.label_choice.setVisible(False)
        self.game_choice.setVisible(False)
        try:
            self.update_bord(True)
        except:
            pass

    def chess_start(self):
        text, ok = QInputDialog.getText(self, 'Название игры', 'Введи название партии:')
        if ok:
            if len(text) > 40 or len(text) < 4:
                QMessageBox.critical(self, 'Ошибка!', 'Диапазон названия: от 4 до 40 символов', QMessageBox.Ok)
                return
            con = self.sql_base
            cur = con.cursor()
            max_id = cur.execute("""SELECT MAX(id) FROM Games""").fetchone()[0]
            plays = set()
            for i in cur.execute("""SELECT play_name FROM Games""").fetchall():
                plays.add(i[0])
            if text in plays:
                self.name = text + str(max_id + 1)
                QMessageBox.warning(self, 'Это название уже есть!', 'Партии будет присвоено название: ' + self.name, QMessageBox.Ok)
            else:
                self.name = text
                QMessageBox.warning(self, 'Название партии!', 'Название партии: ' + self.name, QMessageBox.Ok)

        else:
            return
        self.status = "chess"
        self.steps_list = list()
        self.boards_list = list()
        self.table.setVisible(True)
        self.table_btn2.setText("Сдаться")
        self.table_btn2.setVisible(True)
        self.chess_choice.setVisible(False)
        self.label_choice.setVisible(False)
        self.game_choice.setVisible(False)
        self.active = None
        self.board = chess.Board()
        self.update_bord(True)
        self.findChild(QLabel, 'label_caption').setVisible(True)
        self.exit_bt.setText('В главное меню')

    def caption_about_game(self, text=''):
        print(text)
        if 'char' in text or ('None' in text):
            return
        elif ('закончена' in text) and ('None' not in text):
            print(text, 1)
            if '2' in text:
                self.findChild(QLabel, 'label_caption').setText(text[:-1] + ' белых')
            elif '1' in text:
                self.findChild(QLabel, 'label_caption').setText(text[:-1] + ' черных')
            else:
                self.findChild(QLabel, 'label_caption').setText(text)
            return
        print(text, 2)
        color = self.board.color
        color = '♘ Ход белых. ' if color == 1 else '♞ Ход черных. '
        self.findChild(QLabel, 'label_caption').setText(color + text)

    def to_menu(self):
        self.table_btn2.setVisible(False)
        self.table_btn1.setVisible(False)
        self.table.setVisible(False)
        self.findChild(QLabel, 'label_caption').setVisible(False)
        self.game_choice.setVisible(True)
        self.chess_choice.setVisible(True)
        self.label_choice.setVisible(True)
        for i in range(8, 0, -1):
            self.findChild(QLabel, f'{i}').setVisible(False)
        for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            self.findChild(QLabel, f'{i}').setVisible(False)
        for row in range(7, -1, -1):
            for col in range(8):
                self.findChild(QPushButton, f'{row}{col}').setVisible(False)
                figure = str(self.board.cell(row, col))
                style = self.figure_style(figure, [row, col])
                self.findChild(QPushButton, f'{row}{col}').setStyleSheet(style)
                self.findChild(QPushButton, f'{row}{col}').clicked.connect(self.game_chess)

    def end_game(self):
        csvfile = open(f'chess_game/{self.name}.csv', 'w', encoding='utf8')
        writer = csv.writer(csvfile, delimiter=';')
        for i in range(len(self.steps_list)):
            writer.writerow([self.steps_list[i], self.boards_list[i]])
        csvfile.close()
        cur = self.sql_base.cursor()
        cur.execute("""INSERT INTO Games (play_name) VALUES ('{}')""".format(self.name))
        self.sql_base.commit()

    def game_chess(self):
        row, col = map(int, list(self.sender().objectName()))
        # выполняем выделение клетки при нажатии
        if not self.board.game:
            return
        if not self.active:
            if self.board.field_color(row, col) == self.board.current_player_color():
                self.sender().setStyleSheet(self.active_style(self.board.cell(row, col)))
                self.active = ''.join([str(row), str(col)])
        elif self.active:
            if self.board.field_color(row, col) == self.board.current_player_color():
                self.findChild(QPushButton, self.active).setStyleSheet(self.figure_style(self.board.cell(*map(int,list(self.active))), list(map(int,list(self.active)))))
                self.sender().setStyleSheet(self.active_style(self.board.cell(row, col)))
                self.active = ''.join([str(row), str(col)])
            elif self.active == self.sender().objectName():
                self.findChild(QPushButton, self.active).setStyleSheet(self.figure_style(self.board.cell(*map(int,list(self.active))), [row, col]))
                self.active = None
            else:
                # выполняем обработку хода пользователя
                row1, col1 = int(self.active[0]), int(self.active[1])
                row, col, row1, col1 = row1, col1, row, col
                try:
                    self.step_in_chess(row, col, row1, col1)
                except Exception as eror:
                    self.caption_about_game(str(eror))
                    if not self.board.game:
                        self.steps_update(row, col, row1, col1)
                        self.update_bord(False, str(eror))
                    elif 'шах' in str(eror):
                        self.steps_update(row, col, row1, col1)
                        self.update_bord(False, str(eror))
        if not self.board.game:
            self.end_game()

    def step_in_chess(self, row, col, row1, col1):
        if self.board.field[row][col].char() == 'K':
            if self.board.castling0(row, col, row1, col1):
                self.steps_update(row, col, row1, col1, '0-0-0')
                self.active = None
                self.update_bord()
                return
            elif self.board.castling7(row, col, row1, col1):
                self.steps_update(row, col, row1, col1, '0-0')
                self.active = None
                self.update_bord()
                return

        if self.board.field[row][col].char() == 'P' and (row1 == 7 or row1 == 0):
            if self.board.field[row][col].can_move(self.board, row, col, row1, col1) or self.board.field[row][col].can_attack(self.board, row, col, row1, col1):
                d = {"Ферзь": "Q", "Ладья": "R", "Конь": "N", "Слон": "B"}
                figure, ok_pressed = QInputDialog.getItem(self, "Выбери фигуру", "Выбери фигуру:", list(d), 0, False)
                if ok_pressed:
                    self.board.move_and_promote_pawn(row, col, row1, col1, d[figure])
                    self.steps_update(row, col, row1, col1, d[figure])
        elif self.board.move_piece(row, col, row1, col1):
            self.steps_update(row, col, row1, col1)
        self.active = None
        self.update_bord()

    def good_bye(self):
        if self.status != "menu":
            self.status = "menu"
            self.exit_bt.setText("Закрыть игру")
            self.to_menu()
            self.table.clear()
            self.table_btn2.setText("Удалить")
            self.name = None
        else:
            sys.exit(app.exec())

    def steps_update(self, row, col, row1, col1, text=''):
        d = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        if '0-0' in text:
            self.steps_list.append(text)
        else:
            if self.board.field[row1][col1]:
                s = self.board.field[row1][col1].char() + ' ' + d[col] + str(row + 1) + '-' + d[col1] + str(row1 + 1)
                self.steps_list.append(s + text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ChessBoard()
    ex.show()
    sys.exit(app.exec())
