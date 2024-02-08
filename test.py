import sys

from widgets import *


class Question(QDialog):
    def __init__(self, title="", questions=""):
        super().__init__()
        self.resize(200, 93)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle(title)
        self.setStyleSheet("background-color:white;")
        self.inputLine = QLineEdit(self)
        self.inputLine.setFont(QFont("Microsoft YaHei UI", 9))
        self.inputLine.move(10, 30)
        self.inputLine.resize(175, 25)
        self.inputLine.setStyleSheet("""border-radius:3px;
    border:2px solid rgb(50, 93, 136);
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")
        l = QLabel(questions, self)
        l.setFont(QFont("Microsoft YaHei UI", 9))
        l.move(10, 10)
        self.result = ("", False)
        ok = OutlineButton("确定", self)
        ok.move(60, 60)
        ok.resize(60, 25)
        ok.setStyleSheet(STYLE_SHEET)
        ok.clicked.connect(self.ok)
        cancel = OutlineButton("取消", self)
        cancel.move(125, 60)
        cancel.resize(60, 25)
        cancel.setStyleSheet(STYLE_SHEET)
        cancel.clicked.connect(self.cancel)
        self.exec()

    def ok(self):
        self.result = (self.inputLine.text(), True)
        self.close()

    def cancel(self):
        self.result = (self.inputLine.text(), False)
        self.close()


def question(title, question):
    window = Question(title, question)
    return window.result


class information(QDialog):
    def __init__(self, title="", questions=""):
        super().__init__()
        self.resize(200, 93)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle(title)
        self.setStyleSheet("background-color:white;")
        l = QLabel(questions, self)
        l.setFont(QFont("Microsoft YaHei UI", 9))
        l.move(50, 17)
        photo = QLabel("", self)
        photo.setPixmap(QPixmap(".\\icon\\information.png"))
        photo.move(10, 10)
        cancel = OutlineButton("确定", self)
        cancel.move(125, 60)
        cancel.resize(60, 25)
        cancel.setStyleSheet(STYLE_SHEET)
        cancel.clicked.connect(self.close)
        self.exec()


class critical(QDialog):
    def __init__(self, title="", questions=""):
        super().__init__()
        self.resize(200, 93)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle(title)
        self.setStyleSheet("background-color:white;")
        l = QLabel(questions, self)
        l.setFont(QFont("Microsoft YaHei UI", 9))
        l.move(50, 17)
        photo = QLabel("", self)
        photo.setPixmap(QPixmap(".\\icon\\error.png"))
        photo.move(10, 10)
        cancel = OutlineButton("确定", self)
        cancel.move(125, 60)
        cancel.resize(60, 25)
        cancel.setStyleSheet(STYLE_SHEET)
        cancel.clicked.connect(self.close)
        self.exec()


class Ok(QDialog):
    def __init__(self, title="", questions=""):
        super().__init__()
        self.resize(200, 93)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle(title)
        self.setStyleSheet("background-color:white;")
        l = QLabel(questions, self)
        l.setFont(QFont("Microsoft YaHei UI", 9))
        l.move(50, 17)
        photo = QLabel("", self)
        photo.setPixmap(QPixmap(".\\icon\\question.png"))
        photo.move(10, 10)
        self.result = False
        ok = OutlineButton("确定", self)
        ok.move(60, 60)
        ok.resize(60, 25)
        ok.setStyleSheet(STYLE_SHEET)
        ok.clicked.connect(self.ok)
        cancel = OutlineButton("取消", self)
        cancel.move(125, 60)
        cancel.resize(60, 25)
        cancel.setStyleSheet(STYLE_SHEET)
        cancel.clicked.connect(self.cancel)
        self.exec()

    def ok(self):
        self.result = True
        self.close()

    def cancel(self):
        self.result = False
        self.close()


def ok(title, questions):
    return Ok(title, questions).result


a = QApplication([])
print(information("111", "222"))
sys.exit(a.exec())
