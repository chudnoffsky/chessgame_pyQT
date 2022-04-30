from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QDesktopWidget, QListWidget
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(QWidget):
    def initUI(self):
        self.start_program()
        self.showFullScreen()

    def start_program(self):
        # главное меню
        self.setStyleSheet("""
            * {
                font-size: 20px;
            }
            QPushButton {
                background-color: beige;
            }
            QLabel {
                background: #ced23a;
                text-align: right;
                padding: 10px;
                border-radius: 20px;
            }
            QPushButton#okButton {
                background-color: green;
            }
        """)
        #
        self.size = QDesktopWidget().availableGeometry()
        self.size = self.size.width(), self.size.height()
        self.setGeometry(0, 0, self.size[0], self.size[1])
        self.setWindowTitle("Шахматная доска")
        self.draw_chess()

        self.label_choice = QLabel(self)
        self.label_choice.setText("Меню:")
        size = self.size[0] * 0.3, self.size[1] * 0.1
        y = size[1]

        self.label_choice.setGeometry(((self.size[0] // 2) - (size[0] // 2)), y, size[0], size[1])
        self.label_choice.setAlignment(QtCore.Qt.AlignCenter)
        y += size[1] * 2

        self.chess_choice = QPushButton('Шахматы (на 2 игрока)', self)
        self.chess_choice.setGeometry(((self.size[0] // 2) - (size[0] // 2)), y, size[0], size[1])
        y += size[1] * 2

        self.game_choice = QPushButton('Выбрать партию', self)
        self.game_choice.setGeometry(((self.size[0] // 2) - (size[0] // 2)), y, size[0], size[1])

        self.exit_bt = QPushButton('Закрыть игру', self)
        self.exit_bt.setGeometry(((self.size[0] // 2) - (size[0] // 2)), self.size[1] - size[1], size[0], size[1])

        self.table = QListWidget(self)
        self.table.setGeometry(((self.size[0] // 2) + (size[0] // 3)), (min(self.size) * 0.7) // 8, size[0] * 1.2,
                               self.size[1] * 0.7)
        self.table.setVisible(False)

        self.table_btn1 = QPushButton('Выбрать', self)
        self.table_btn1.setGeometry(((self.size[0] // 2) + (size[0] // 3)), (min(self.size) * 0.7 + self.size[1] * 0.1),
                                    size[0] * 0.5, size[1] * 0.5)
        self.table_btn1.setVisible(False)

        self.table_btn2 = QPushButton('Удалить', self)
        self.table_btn2.setGeometry(((self.size[0] // 2) + (size[0] // 3) + size[0] * 0.7),
                                    (min(self.size) * 0.7 + self.size[1] * 0.1), size[0] * 0.5, size[1] * 0.5)
        self.table_btn2.setVisible(False)

    def draw_caption(self, size):
        k = 0.7
        x = (self.size[0] * (1 - k)) // 2 - size[0]
        label = QLabel('Ход белых:', self)
        label.setObjectName('label_caption')
        label.setGeometry(x, 0, size[0] * 8, size[1])
        label.setStyleSheet("""
        QLabel {
            background: Bisque	;
            padding: 10px;
            border-radius: 20px;
        }""")
        label.setVisible(False)
        label.setAlignment(QtCore.Qt.AlignCenter)

        for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            y = size[1] * 9
            label = QLabel(i, self)
            label.setObjectName(f'{i}')
            label.setText(i)
            label.setGeometry(x, y, size[0], size[1] // 2)
            label.setStyleSheet("""
            QLabel {
                background: #ced23a;
                padding: 10px;
                border-radius: 20px;
            }""")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setVisible(False)
            x += size[0]

        y = size[1]
        x = round((self.size[0] * (1 - k)) // 2 - size[0] * 1.5)

        for i in range(8, 0, -1):
            i = str(i)
            label = QLabel(i, self)
            label.setText(i)
            label.setObjectName(f'{i}')
            label.setGeometry(x, y, size[0] // 2, size[1])
            label.setStyleSheet("""
            QLabel {
                background: #ced23a;
                padding: 10px;
                border-radius: 20px;
            }""")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setVisible(False)
            y += size[0]

    def draw_chess(self):
        k = 0.7
        size = min(self.size)
        size = (size * k) // 8, (size * k) // 8
        self.draw_caption(size)

        y = 0

        for i in range(7, -1, -1):
            x = ((self.size[0] * (1 - k)) // 2) - size[0]
            y += size[1]
            for j in range(8):
                btn = QPushButton(self)
                btn.setObjectName(f'{i}{j}')
                btn.setGeometry(x, y, size[0], size[1])
                btn.setVisible(False)
                x += size[0]

    def active_style(self, figure):
        figure = figure.replace(' ', '1')

        style = f"""
            background-image: url(img/chess/{figure}.png);
            background-repeat: no-repeat-y;
            background-position: center;
            padding: 10px;
            outline: 3px;
            border-radius: 20px;
            background-color: orange;
            """
        style = '* {\n' + style + '\n }'
        return style

    def figure_style(self, figure, color=[]):
        figure = figure.replace(' ', '1')

        if color:
            color = sum(color) % 2 == 0
            if color:
                color = 'background-color: SaddleBrown'
            else:
                color = 'background-color: BurlyWood'

        style = f"""
            background-image: url(img/chess/{figure}.png);
            background-repeat: no-repeat-y;
            background-position: center;
            {color}
            """
        style = '* {\n' + style + '\n }'

        style += '''
        * :hover {
            text-align: right;
            background-color: yellow;
            padding: 10px;
            outline: 3px;
            border-radius: 20px;}'''
        return style
