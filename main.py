# !/usr/bin/python3
# coding: GBK
import os
import random
import subprocess
import threading
import webbrowser

import jieba
import pyperclip

from widgets import *
import datetime
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


# from qt_material import apply_stylesheet


def get_path():
    try:
        a = sys.argv[1]
    except IndexError:
        a = None
    if a is None:
        try:
            with open(f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad.tmp", "rt") as fo:
                paths = fo.read()
                fo.close()
        except FileNotFoundError:
            with open(f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad.tmp", "wt") as fo:
                paths = ""
                fo.close()
        if not (os.path.isfile(paths)):
            paths = ""
    else:
        paths = a
    nams = os.path.basename(paths)
    if nams == "" or nams is None:
        nams = "无标题"
    return paths


def add_cascade(parents: QMenuBar, label: str = '', icon=None) -> QMenuBar:
    return parents.addMenu(label)


def add_command(parents: QMenuBar, label: str = '', command=lambda: None, icon: QIcon = QIcon(),
                shortcut: str = '') -> QMenuBar:
    act = QAction(label, parents)
    act.setIcon(icon)
    act.setShortcut(shortcut)
    act.triggered.connect(command)
    parents.addAction(act)
    return act


def critical(title, message):
    messageBox = QMessageBox(QMessageBox.Icon.Critical, title, message)
    messageBox.setStyleSheet(WIDGET_STYLE_SHEET)
    messageBox.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
    btn = CursorChangeButton("确定", None)
    btn.resize(30, 60)
    Qyes = messageBox.addButton(btn, QMessageBox.YesRole)
    # Qno = messageBox.addButton(self.tr("忽略"), QMessageBox.NoRole)
    messageBox.exec_()


def information(title, message):
    messageBox = QMessageBox(QMessageBox.Icon.Information, title, message)
    messageBox.setStyleSheet(WIDGET_STYLE_SHEET)
    messageBox.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
    btn = CursorChangeButton("确定", None)
    btn.resize(30, 60)
    Qyes = messageBox.addButton(btn, QMessageBox.YesRole)
    # Qno = messageBox.addButton(self.tr("忽略"), QMessageBox.NoRole)
    messageBox.exec_()
    # if messageBox.clickedButton() == Qyes:
    #     return True
    # else:


class MainWindow(QMainWindow):
    """docstring for MainWindow"""
    text: list[TextEdit]
    menu: QMenuBar

    def __init__(self):
        super().__init__()
        self.resize(1300, 700)
        with open("style.qss") as fo:
            self.setStyleSheet(fo.read())
        self.setWindowIcon(QIcon(".//icon//notepad.ico"))
        # self.setWindowTitle("python记事本")
        self.menu = self.menuBar()
        self.menu.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.note = QTabWidget(self)
        self.note.setFont(FONT)
        self.note.resize(950, 580)
        self.note.setStyleSheet("QTabBar::tab {width:250px;}"
                                "QTabBar::tab::hover{background-color:rgb(151, 198, 235)}")
        self.note.move(150, 30)
        self.text = []
        get = get_path()
        self.paths = [get]
        self.tab_button = []
        self.disabled = []
        # threading.Thread(target=self.add_menu).start()
        self.right = self.note.tabBar().RightSide
        self.add_menu()
        self.note.tabBar().setMovable(True)
        self.settings = CursorChangeButton('', self)
        self.settings.setStyleSheet("background-color:rgba(0, 0, 0, 0)")
        self.settings.setIcon(QIcon(".\\icon\\settings.png"))
        self.settings.move(1230, 0)
        self.settings.clicked.connect(lambda: Setting(self))
        self.file_area = QScrollArea(self)
        self.file_area.setFont(FONT_)
        self.file_area.setFrameShape(QFrame.NoFrame)
        self.file_area.move(0, 50)
        if self.paths[0] == '':
            self.new()
        else:
            self.start()
        self.file_num = QLabel(f"  共{len(self.text[-1].toText())}个字符  ", self)
        # self.file_num.setFont(FONT_)
        font_ = QFont()
        font_.setFamily("Microsoft YaHei UI")
        font_.setPointSize(9)
        self.file_num.setFont(font_)
        self.row_column = QLabel("  第1行,第1列  ", self)
        self.row_column.setFont(font_)
        self.zoomed = QLabel("  100%  ", self)
        self.zoomed.setFont(font_)
        font_.setPointSize(15)
        font_.setBold(True)
        self.statusBar().addPermanentWidget(self.row_column)
        self.statusBar().addPermanentWidget(self.zoomed)
        self.statusBar().addPermanentWidget(self.file_num)
        opened_file = QLabel("打开的文件", self)
        opened_file.setFont(font_)
        opened_file.move(0, 20)
        self.add = CursorChangeButton("+", self)
        self.add.move(1240, 35)
        self.add.resize(20, 20)
        self.add.setFont(FONT)
        self.add.setStyleSheet("background-color: rgba(0, 0, 0, 0);color: rgb(100, 100, 3);")
        self.add.clicked.connect(self.new)
        self.file = CursorChangeButton("▼", self)
        self.file.move(1270, 35)
        self.file.resize(20, 20)
        self.file.setFont(FONT)
        self.file.setStyleSheet("background-color: rgba(0, 0, 0, 0);color: rgb(100, 100, 3);")
        self.file.clicked.connect(self.show_file)
        self.file_menu = QMenu(self)
        self.file_menu.move(1270, 35)
        self.file_menu.hide()
        self.setAcceptDrops(True)
        self.dir = FileTreeWidget(self)
        self.dir.move(-10, 300)
        self.dir.resize(160, self.height() - 330)
        self.note.currentChanged[int].connect(
            lambda e=None: threading.Thread(target=self.show_status).start() or self.setWindowTitle(
                f"python记事本 - {os.path.basename(self.paths[self.note.currentIndex()])}"))
        self.show_status()
        self.show()

    def show_status(self):
        try:
            self.statusBar().showMessage(self.paths[self.note.currentIndex()])
            self.file_num.setText(f"  共{len(self.text[self.note.currentIndex()].toText())}个字符  ")
        except IndexError:
            pass
        if isinstance(self.text[self.note.currentIndex()], TextEdit):
            for i in self.disabled: i.setDisabled(False)
            # map(lambda i: i.setDisabled(False), self.disabled)
        else:
            for i in self.disabled: i.setDisabled(True)
            # map(lambda i: i.setDisabled(True), self.disabled)

    def highlight(self, text):
        lexer = PythonLexer()
        formatter = HtmlFormatter(style='colorful')
        html = highlight(text.toPlainText(), lexer, formatter)
        css = formatter.get_style_defs('.highlight')
        text.setHtml("<style>" + css + "</style>" + html)

    def dragEnterEvent(self, e):
        print(e.mimeData().text()[8:])
        self.paths.append(e.mimeData().text()[8:])
        self.start()
        # super().dragEnterEvent(e)

    def show_file(self):
        self.file_menu.clear()
        commands = [w for w in range(self.note.count())]
        for i in range(len(self.paths)):
            if os.path.isfile(self.paths[i]):
                add_command(self.file_menu, label=os.path.basename(self.paths[i]),
                            command=lambda s=None, f=commands[i]: self.current_with_debug(f))
            else:
                add_command(self.file_menu, label="无标题",
                            command=lambda s=None, f=commands[i]: self.current_with_debug(f))
        self.file_menu.move(self.file.x() + self.x(), self.file.y() + self.y())
        self.file_menu.show()

    def event(self, event: QEvent):
        if event.type() == event.StatusTip:
            if event.tip() == "":
                event = QStatusTipEvent(self.paths[self.note.currentIndex()])  # 此处为要始终显示的内容
        if hasattr(self, "file_num"):
            self.file_num.setText(f"  共{len(self.text[self.note.currentIndex()].text.toPlainText())}个字符  ")
        return super().event(event)

    def current_with_debug(self, w):
        self.note.setCurrentIndex(w)
        print(w)

    def update_file(self):
        self.file_area.destroy()
        self.file_area = QScrollArea(self)
        self.file_area.setFont(FONT_)
        self.file_area.setFrameShape(QFrame.NoFrame)
        self.file_area.move(0, 50)
        self.file_area.resize(150, 300)
        self.file_area.show()
        commands = [w for w in range(self.note.count())]
        x = 0
        for i in range(len(self.paths)):
            if os.path.isfile(self.paths[i]):
                btn = CursorChangeButton(os.path.basename(self.paths[i]), self.file_area)
                btn.setStyleSheet("background-color:rgb(255, 255, 255);border:2px solid #FFFFFF;")
                btn.move(10, x * 35)
                btn.clicked.connect(
                    lambda signal=None, f=commands[i]: self.current_with_debug(f) and self.statusBar().showMessage(
                        self.paths[self.note.currentIndex()]))
                btn.setFont(FONT_)
                btn.show()
                x += 1

    # noinspection
    def zoom(self, add: int):
        global FONT
        if (add == 0):
            FONT.setPointSize(12)
        else:
            size = FONT.pointSize() + add
            size = size if size >= LAST_FONT_SIZE else size + 1
            size = size if size <= 108 else size - 1
            FONT.setPointSize(size)
        for i in self.text:
            i.text.setFont(FONT)
        self.zoomed.setText(f"  {int(FONT.pointSize() * 100 / 12)}%  ")

    def add_menu(self):
        file = add_cascade(self.menu, "文件(F)")
        add_command(file, label="新建(N)", shortcut="Ctrl+N", command=self.new)
        add_command(file, label="新建窗口", command=lambda: os.system(sys.argv[0]))
        file.addSeparator()
        add_command(file, label="打开(O)", shortcut="Ctrl+O",
                    command=lambda: threading.Thread(target=self.open).start())
        encoding = add_cascade(file, label="用...打开")
        encodings = ("ANSI", "ASCII", "GBK", "GB2312", "UTF-8", "UTF-16", "Latin-1")
        commands = [lambda: self.open_as(i) for i in encodings]
        for i in range(len(encodings)):
            add_command(encoding, label=f"用{encodings[i]}打开", command=commands[i])
        explorer = add_cascade(file, "文件路径")
        add_command(explorer, label="复制文件名",
                    command=lambda: pyperclip.copy(os.path.basename(self.paths[self.note.currentIndex()])))
        add_command(explorer, label="复制文件路径",
                    command=lambda: pyperclip.copy(os.path.dirname(self.paths[self.note.currentIndex()])))
        add_command(explorer, label="复制文件名和路径",
                    command=lambda: pyperclip.copy(self.paths[self.note.currentIndex()]))
        add_command(explorer, label="打开文件路径", command=lambda: subprocess.Popen(
            f"explorer.exe {os.path.dirname(self.paths[self.note.currentIndex()])}"))
        file.addSeparator()
        info = add_cascade(file, label="文件信息")
        self.disabled += [
            add_command(info, label="文本长度", command=lambda: information("文本长度",
                                                                            f"当前文本长度为: {len(self.text[self.note.currentIndex()].toText())}")),
            add_command(info, label="文本行数", command=lambda: information("文本行数",
                                                                            "当前文本行数为: {}".format(self.text[
                                                                                self.note.currentIndex()].toText().count(
                                                                                '\n'))))]
        add_command(info, label="文件统计", command=lambda: FileStatistic(self.paths))
        self.disabled.append(
            add_command(file, label="词频统计", command=lambda: threading.Thread(target=self.lcut).start()))
        file.addSeparator()
        self.disabled += [add_command(file, label="保存(S)", shortcut="Ctrl+S", command=self._save),
                          add_command(file, label="全部保存", command=self._save_all),
                          add_command(file, label="另存为", shortcut="Ctrl+Shift+S", command=self._save_as)]
        add_command(file, label="复制文件", command=self._save_as)
        file.addSeparator()
        add_command(file, label="关闭选项卡(W)", shortcut="Ctrl+W",
                    command=lambda: self.close_tab(self.note.currentIndex()))
        add_command(file, label="退出", shortcut="Alt+F4", command=QApplication.instance().quit)
        edit = add_cascade(self.menu, "编辑(E)")
        self.disabled += [
            add_command(edit, label="插入当前时间",
                        command=lambda: self.text[self.note.currentIndex()].text.textCursor().insertText(
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            add_command(edit, label="web上搜索",
                        command=self.search_web)]
        edit.addSeparator()
        h = add_cascade(edit, label="行")
        self.disabled.append(h)
        for text, command in (
                ("增加行", lambda: self.text[self.note.currentIndex()].text.textCursor().insertText("\n")),
                ("删除行", self.delete),
                ("行排序(升序)", self.sort),
                ("行排序(降序)", lambda: self.sort(reverse=True)),
                ("行逆序", self.reverse),
                ("行打乱", self.shuffle),
                ("行去重", self.deduplication)):
            self.disabled.append(add_command(h, label=text, command=command))
        self.disabled += [
            add_command(edit, label="跳转到行", command=lambda: self.text[self.note.currentIndex()].text.goToLine(
                QInputDialog.getText(MSG_WIDGET, "跳转", "请输入跳转到行: ")), shortcut="Ctrl+G"),
            add_command(edit, label="跳转到开头", command=lambda: self.text[self.note.currentIndex()].text.goToLine(1),
                        shortcut="Home"),
            add_command(edit, label="跳转到结尾", command=lambda: self.text[self.note.currentIndex()].text.goToEnd(),
                        shortcut="End")]
        edit.addSeparator()
        for text, command, shortcut in (
                ("增加缩进", self.add_tab, "Ctrl+]"),
                ("减少缩进", self.remove_tab, "Ctrl+[")
        ):
            self.disabled.append(add_command(edit, label=text, command=command, shortcut=shortcut))
        edit.addSeparator()
        up = add_cascade(edit, label="大小写转换")
        self.disabled.append(up)
        self.disabled += [
            add_command(up, label="转换成大写", command=lambda: self.big_small(low=False)),
            add_command(up, label="转换成小写", command=lambda: self.big_small(low=True)),
            add_command(up, label="首字母大写", command=lambda: self.big_small(low='')),
            add_command(up, label="反向处理", command=lambda: self.big_small(low=None))]
        zoom = add_cascade(edit, label="缩放")
        self.disabled.append(zoom)
        self.disabled += [
            add_command(zoom, label="增大", command=lambda: self.zoom(1), shortcut="Ctrl++"),
            add_command(zoom, label="减小", command=lambda: self.zoom(-1), shortcut="Ctrl+-"),
            add_command(zoom, label="恢复", command=lambda: self.zoom(0), shortcut="Ctrl+0")]
        edit.addSeparator()
        self.disabled += [
            add_command(edit, label="复制(C)",
                        command=lambda: pyperclip.copy(
                            self.text[self.note.currentIndex()].text.textCursor().selectedText()), shortcut="Ctrl+C"),
            add_command(edit, label="剪切(X)", command=self.cut, shortcut="Ctrl+X"),
            add_command(edit, label="粘贴(V)",
                        command=lambda:
                        self.text[self.note.currentIndex()].text.textCursor().insertText(pyperclip.paste()),
                        shortcut="Ctrl+V"),
            add_command(edit, label="查找(F)", command=self.Find_UI, shortcut="Ctrl+F"),
            add_command(edit, label="替换(H)", command=self.Replace_UI, shortcut="Ctrl+H"),
            add_command(edit, label="撤销(Z)", command=lambda: self.text[self.note.currentIndex()].text.undo(),
                        shortcut="Ctrl+Z"),
            add_command(edit, label="重做(Y)", command=lambda: self.text[self.note.currentIndex()].text.redo(),
                        shortcut="Ctrl+Y"),
            add_command(edit, label="全选(A)", command=lambda: self.text[self.note.currentIndex()].text.selectAll(),
                        shortcut="Ctrl+A"),
            add_command(edit, label="删除",
                        command=lambda: self.text[self.note.currentIndex()].text.textCursor().removeSelectedText(),
                        shortcut='Delete'),
            add_command(edit, label="清空", command=lambda: self.text[self.note.currentIndex()].text.clear())]
        help_ = add_cascade(self.menu, "帮助(H)")
        add_command(help_, label="设置", command=lambda: Setting(self))
        add_command(help_, label="关于",
                    command=lambda: information("关于", """python记事本1.0.0
Copyright(2023)"""))

    def Find_UI(self):
        self.findDialog = QDialog(self)
        self.findDialog.setStyleSheet(WIDGET_STYLE_SHEET)
        self.findDialog.setWindowTitle("查找")
        self.findDialog.setFixedSize(380, 80)

        self.labelFind = QLabel(self.findDialog)
        self.labelFind.setText("查找内容(&N):")
        self.labelFind.setGeometry(10, 10, 70, 20)

        self.lineEditFind = QLineEdit(self.findDialog)
        self.lineEditFind.setGeometry(90, 10, 180, 25)
        # self.lineEditFind.setText(self.fintText)

        self.labelFind.setBuddy(self.lineEditFind)

        self.pushButtonFind = OutlineButton(self.findDialog)
        self.pushButtonFind.setText("查找下一个(&F)")
        self.pushButtonFind.setGeometry(280, 10, 90, 25)
        self.pushButtonFind.clicked.connect(self.find)

        self.pushButtonFindClose = OutlineButton(self.findDialog)
        self.pushButtonFindClose.setText("取消")
        self.pushButtonFindClose.setGeometry(280, 40, 90, 25)
        self.pushButtonFindClose.clicked.connect(self.findClose)

        self.checkBoxCase = QCheckBox(self.findDialog)
        self.checkBoxCase.setText("区分大小写(&C)")
        self.checkBoxCase.setGeometry(10, 50, 100, 20)

        self.groupBoxFind = QGroupBox(self.findDialog)
        self.groupBoxFind.setTitle("方向")
        self.groupBoxFind.setGeometry(110, 35, 160, 40)

        self.radioButtonFindProv = QRadioButton(self.groupBoxFind)
        self.radioButtonFindProv.setText("向上(&U)")
        self.radioButtonFindProv.setGeometry(10, 15, 60, 20)

        self.radioButtonFindNext = QRadioButton(self.groupBoxFind)
        self.radioButtonFindNext.setText("向下(&D)")
        self.radioButtonFindNext.setGeometry(90, 15, 60, 20)
        self.radioButtonFindNext.setChecked(True)

        self.findDialog.show()

    def Replace_UI(self):
        self.replaceDialog = QDialog(self)
        self.replaceDialog.setStyleSheet(WIDGET_STYLE_SHEET)
        self.replaceDialog.setWindowTitle("替换")
        self.replaceDialog.setFixedSize(380, 130)

        self.labelFind = QLabel(self.replaceDialog)
        self.labelFind.setText("查找内容(&N):")
        self.labelFind.setGeometry(10, 10, 70, 20)

        self.lineEditFind = QLineEdit(self.replaceDialog)
        self.lineEditFind.setGeometry(90, 10, 180, 25)
        # self.lineEditFind.setText(self.fintText)

        self.labelFind.setBuddy(self.lineEditFind)

        self.labelReplace = QLabel(self.replaceDialog)
        self.labelReplace.setText("替换(&P):")
        self.labelReplace.setGeometry(10, 40, 70, 20)

        self.lineEditReplace = QLineEdit(self.replaceDialog)
        self.lineEditReplace.setGeometry(90, 40, 180, 25)
        # self.lineEditReplace.setText(self.replaceText)

        self.labelReplace.setBuddy(self.lineEditReplace)

        self.pushButtonFind = OutlineButton(self.replaceDialog)
        self.pushButtonFind.setText("查找下一个(&F)")
        self.pushButtonFind.setGeometry(280, 10, 90, 25)
        self.pushButtonFind.clicked.connect(self.find)

        self.pushButtonReplace = OutlineButton(self.replaceDialog)
        self.pushButtonReplace.setText("替换(&R)")
        self.pushButtonReplace.setGeometry(280, 40, 90, 25)
        self.pushButtonReplace.clicked.connect(self.replace)

        self.pushButtonReplaceAll = OutlineButton(self.replaceDialog)
        self.pushButtonReplaceAll.setText("全部替换(&A)")
        self.pushButtonReplaceAll.setGeometry(280, 70, 90, 25)
        self.pushButtonReplaceAll.clicked.connect(lambda: self.replace(True))

        self.pushButtonFindClose = OutlineButton(self.replaceDialog)
        self.pushButtonFindClose.setText("取消")
        self.pushButtonFindClose.setGeometry(280, 100, 90, 25)
        self.pushButtonFindClose.clicked.connect(self.replaceClose)

        self.checkBoxCase = QCheckBox(self.replaceDialog)
        self.checkBoxCase.setText("区分大小写(&C)")
        self.checkBoxCase.setGeometry(10, 100, 100, 20)

        self.groupBoxFind = QGroupBox(self.replaceDialog)
        self.groupBoxFind.setTitle("方向")
        self.groupBoxFind.setGeometry(110, 85, 160, 40)

        self.radioButtonFindProv = QRadioButton(self.groupBoxFind)
        self.radioButtonFindProv.setText("向上(&U)")
        self.radioButtonFindProv.setGeometry(10, 15, 60, 20)

        self.radioButtonFindNext = QRadioButton(self.groupBoxFind)
        self.radioButtonFindNext.setText("向下(&D)")
        self.radioButtonFindNext.setGeometry(90, 15, 60, 20)
        self.radioButtonFindNext.setChecked(True)

        self.replaceDialog.show()

    def find(self):
        text = self.text[self.note.currentIndex()]
        self.fintText = self.lineEditFind.text()
        if self.fintText == "":
            QMessageBox.information(self, "python记事本", "请输入搜索内容")
            return False
        # if self.radioButtonFindNext.isChecked():
        #     QMessageBox.information(self, "python记事本", "目前向上查找还在测试中")
        #     return False
        if self.checkBoxCase.isChecked() and self.radioButtonFindProv.isChecked():
            result = text.find(self.fintText,
                               QTextDocument.FindCaseSensitively | QTextDocument.FindBackward)
        elif self.checkBoxCase.isChecked() and self.radioButtonFindNext.isChecked():
            result = text.find(self.fintText, QTextDocument.FindCaseSensitively)
        elif self.checkBoxCase.isChecked() == False and self.radioButtonFindProv.isChecked():
            result = text.find(self.fintText, QTextDocument.FindBackward)
        else:
            result = text.find(self.fintText)

        if not result:
            QMessageBox.information(self, "记事本", "找不到\"" + self.fintText + "\"")

        return result

    def replace(self, All=False):
        text = self.text[self.note.currentIndex()].text
        if not self.find():
            return False
        if self.radioButtonFindNext.isChecked():
            QMessageBox.information(self, "python记事本", "目前向上查找还在测试中")
            return False
        self.replaceText = self.lineEditReplace.text()
        if self.replaceText == "":
            QMessageBox.information(self, "python记事本", "请输入替换内容")
            return False

        if All:
            result = text.toPlainText().replace(self.fintText, self.replaceText)
            text.setPlainText(result)
        else:
            text.cut()
            text.insertPlainText(self.replaceText)

    def findClose(self):
        self.findDialog.close()

    def replaceClose(self):
        self.replaceDialog.close()

    def big_small(self, low=True):
        text = self.text[self.note.currentIndex()]
        if low:
            get = str(text.textCursor().selectedText())
            print(get)
            text.textCursor().removeSelectedText()
            text.textCursor().insertText(get.lower())
        elif low is None:
            get = str(text.textCursor().selectedText())
            text.textCursor().removeSelectedText()
            for i in get:
                if 65 <= ord(i) <= 90:
                    text.textCursor().insertText(i.lower())
                else:
                    text.textCursor().insertText(i.upper())
        elif low == '':
            get = str(text.textCursor().selectedText())
            text.textCursor().removeSelectedText()
            text.textCursor().insertText(get[0].upper())
            text.textCursor().insertText(get[1:])
        else:
            get = str(text.textCursor().selectedText())
            text.textCursor().removeSelectedText()
            text.textCursor().insertText(get.upper())

    def delete(self) -> None:
        row = self.text[self.note.currentIndex()].text.textCursor().blockNumber()
        get = self.text[self.note.currentIndex()].toText().split("\n")
        del get[row]
        self._insert(get)

    def add_tab(self) -> None:
        row = self.text[self.note.currentIndex()].text.textCursor().blockNumber()
        get = self.text[self.note.currentIndex()].toText().split("\n")
        get[row] = "    " + get[row]
        self._insert(get)
        self.text[self.note.currentIndex()].text.goToLine(row)

    def remove_tab(self) -> None:
        row = self.text[self.note.currentIndex()].text.textCursor().blockNumber()
        get = self.text[self.note.currentIndex()].toText().split("\n")
        if get[row][0:4] == "    ":
            get[row] = get[row][4:]
        elif get[row][0] == "\t":
            get[row] = get[row][1:]
        self._insert(get)
        self.text[self.note.currentIndex()].text.goToLine(row)

    def search_web(self):
        selected = self.text[self.note.currentIndex()].text.textCursor().selectedText()
        if selected != '':
            webbrowser.open(f"https://cn.bing.com/search?q={selected}")
        else:
            keyword = QInputDialog(MSG_WIDGET).getText(MSG_WIDGET, 'web上搜索', '请输入搜索的内容:')[0]
            if keyword != '':
                webbrowser.open(f"https://cn.bing.com/search?q={keyword}")

    def cut(self):
        text = self.text[self.note.currentIndex()].text.textCursor()
        pyperclip.copy(text.selectedText())
        text.removeSelectedText()

    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.note.resize(self.width() - 150, self.height() - 50)
        self.settings.move(self.width() - 70, 0)
        self.add.move(self.width() - 80, 5)
        self.file.move(self.width() - 60, 5)
        self.file_area.resize(150, 300)
        self.dir.resize(160, self.height() - 310)
        for i in self.text:
            i: TextEdit
            # i.text.move(30,0)
            if isinstance(i, TextEdit):
                try:
                    i.resize(self.note.width() - int(self.text[-1].text.lineNumberArea.width() / 5) - 1,
                             self.note.height() - 45)
                except AttributeError:
                    pass

    def open(self):
        path = FILEDIALOG.getOpenFileNames(MSG_WIDGET)
        print(path)
        if path[-1] != "":
            for i in path[0]:
                self.paths.append(i)
                self.start()
            self.note.setCurrentIndex(self.note.count() - 1)

    def open_as(self, encoding):
        path = FILEDIALOG.getOpenFileNames(MSG_WIDGET)
        print(path)
        if path[-1] != "":
            for i in path[0]:
                self.paths.append(i)
                self.starts(encoding)
            self.note.setCurrentIndex(self.note.count() - 1)

    def _insert(self, get):
        self.text[self.note.currentIndex()].clear()
        self.text[self.note.currentIndex()].append("\n".join(get))

    def sort(self, reverse=False):
        get = self.text[self.note.currentIndex()].toText().split("\n")
        get.sort()
        if reverse:
            get = get[::-1]
        self._insert(get)

    def reverse(self):
        get = self.text[self.note.currentIndex()].toText().split("\n")[::-1]
        self._insert(get)

    def shuffle(self):
        get = self.text[self.note.currentIndex()].toText().split("\n")
        random.shuffle(get)
        self._insert(get)

    def deduplication(self):
        get = self.text[self.note.currentIndex()].toText().split("\n")
        get = list(dict.fromkeys(get))
        self._insert(get)

    @staticmethod
    def saves(string):
        if string != f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad_run_c_error.error" \
                and string != "" \
                and string != f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad_chinese_words_for_15.python_notepad":
            with open(f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad.tmp", "wt") as fo:
                fo.write(string)
                fo.close()

    def start(self):
        is_open = True
        is_photo = self.paths[-1].split(".")[-1].lower() in (
            "jpg", "jpeg", "png", "ico", "bmp", "gif", 'mp3', 'm4a', 'flac', 'wav', 'ogg', "wma", "mp4", "wmv", "webm",
            "mkv")
        if os.path.isfile(self.paths[-1]):
            try:
                with open(self.paths[-1], 'rt', encoding='ANSI') as fo:
                    read = fo.read()
                    self.saves(self.paths[-1])
            except UnicodeError:
                try:
                    with open(self.paths[-1], 'rt', encoding='utf-8') as fo:
                        read = fo.read()
                        self.saves(self.paths[-1])
                except UnicodeError:
                    read = ""
                    if not is_photo:
                        critical("错误", "无法打开此文件! ")
                        is_open = False
                    else:
                        self.saves(self.paths[-1])
        else:
            read = ''
        if is_open:
            if is_photo:
                if self.paths[-1].split(".")[-1].lower() in ('mp3', 'm4a', 'flac', 'wav', 'ogg', 'wma'):
                    text = AudioPlayer(self, self.paths[-1])
                elif self.paths[-1].split(".")[-1].lower() in ("mp4", "wmv", "webm", "mkv"):
                    text = MediaPlayer(self, self.paths[-1])
                else:
                    text = PhotoEdit(self, self.paths[-1])
            else:
                text = TextEdit(self)
            # text.resize(self.note.width(), self.note.height())
            text.append(read)
            text.text.setFont(FONT)
            self.note.addTab(text, os.path.basename(self.paths[-1]))
            self.text.append(text)
            self.tab_button.append(TabButtonWidget(self, self.note.count() - 1))
            self.note.tabBar().setTabButton(self.note.count() - 1, self.right, self.tab_button[-1])
            self.setWindowTitle(f"python记事本 - {os.path.basename(self.paths[self.note.currentIndex()])}")
            threading.Thread(target=lambda: self.note.setCurrentIndex(self.note.count() - 1)).start()
            if isinstance(self.text[-1], TextEdit):
                self.text[-1].text.goToLine(1)
                self.text[-1].resize(self.note.width() - int(self.text[-1].text.lineNumberArea.width() / 5) - 1,
                                     self.note.height() - 45)
            self.statusBar().showMessage(self.paths[-1])
            if os.path.splitext(self.paths[-1])[-1] in (".py", ".pyw", ".pyi"):
                PythonHighlighter(self.text[-1].text.document())
            #     print(1)
            #     self.highlight(self.text[-1].text)
            # self.text[-1].text.setFont(FONT)
            self.text[-1].text.setToolTip(self.paths[-1])
        else:
            del self.paths[-1]
        self.update_file()

    def mousePressEvent(self, *args, **kwargs):
        super().mousePressEvent(*args, **kwargs)
        self.statusBar().showMessage(self.paths[self.note.currentIndex()])
        self.file_num.setText(f"  共{len(self.text[-1].toText())}个字符  ")

    def starts(self, encoding):
        is_open = True
        if os.path.isfile(self.paths[-1]):
            try:
                with open(self.paths[-1], 'rt', encoding=encoding) as fo:
                    read = fo.read()
                    self.saves(self.paths[-1])
            except UnicodeError:
                critical("错误", "无法打开此文件! ")
                is_open = False
        else:
            read = ''
        if is_open:
            text = TextEdit(self)
            # text.resize(self.note.width(), self.note.height())
            text.append(read)
            text.text.setFont(FONT)
            self.note.addTab(text, os.path.basename(self.paths[-1]))
            self.text.append(text)
            self.tab_button.append(TabButtonWidget(self, self.note.count() - 1))
            self.note.tabBar().setTabButton(self.note.count() - 1, self.right, self.tab_button[-1])
            self.setWindowTitle(f"python记事本 - {os.path.basename(self.paths[self.note.currentIndex()])}")
            self.note.setCurrentIndex(self.note.count() - 1)
            self.text[-1].text.goToLine(1)
        else:
            del self.paths[-1]
        self.update_file()

    def _save(self):
        index = self.note.currentIndex()
        if isinstance(self.text[index], TextEdit):
            if os.path.isfile(self.paths[index]):
                with open(self.paths[index], 'wt') as fo:
                    fo.write(self.text[index].toText())
            else:
                path = FILEDIALOG.getSaveFileName(MSG_WIDGET)
                if path[-1] != "":
                    with open(path[0], 'wt') as fo:
                        fo.write(self.text[index].toText())

    def _save_as(self):
        index = self.note.currentIndex()
        if isinstance(self.text[index], TextEdit):
            path = FILEDIALOG.getSaveFileName(MSG_WIDGET)
            if path[-1] != "":
                with open(path[0], 'wt') as fo:
                    fo.write(self.text[index].toText())

    def _save_all(self):
        for index in range(self.note.count()):
            if isinstance(self.text[index], TextEdit):
                if os.path.isfile(self.paths[index]):
                    with open(self.paths[index], 'wt') as fo:
                        fo.write(self.text[index].toText())
                else:
                    path = FILEDIALOG.getSaveFileName(MSG_WIDGET)
                    if path[-1] != "":
                        with open(self.paths[index], 'wt') as fo:
                            fo.write(self.text[index].toText())

    def lcut(self):
        a = jieba.lcut(self.text[self.note.currentIndex()].toText())
        counts = {}
        for word in a:
            if len(word) == 1:
                continue
            else:
                rword = word
            counts[rword] = counts.get(rword, 0) + 1
        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)
        x = ""
        i = 0
        while True:
            try:
                word, count = items[i]
                x += "{0:<10}{1:>5}\n".format(word, count)
            except IndexError:
                break
            i += 1
        print(x)
        ShowTextDialog(title="词频统计", string=x)

    def new(self):
        self.paths.append("")
        text = TextEdit(self)
        # text.resize(self.note.width(), self.note.height())
        text.text.setFont(FONT)
        self.note.addTab(text, "无标题")
        self.text.append(text)
        self.tab_button.append(TabButtonWidget(self, self.note.count() - 1))
        self.note.tabBar().setTabButton(self.note.count() - 1, self.right, self.tab_button[-1])
        self.setWindowTitle("python记事本 - 无标题")
        self.note.setCurrentIndex(self.note.count() - 1)

    def close_tab(self, index: int) -> None:
        self.note.removeTab(index)
        self.text[index].deleteLater()
        del self.paths[index]
        del self.text[index]
        if self.note.count() <= 0:
            self.new()
        for i in self.tab_button:
            if i.index >= index:
                i.index -= 1
        self.update_file()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MSG_WIDGET = QMessageBox()
    MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
    MSG_WIDGET.setFont(FONT_)
    MSG_WIDGET.setStyleSheet(WIDGET_STYLE_SHEET)
    OK_BTN = MSG_WIDGET.addButton("确定", QMessageBox.YesRole)
    CANCEL_BTN = MSG_WIDGET.addButton("取消", QMessageBox.NoRole)
    FILEDIALOG = QFileDialog(None)
    FILEDIALOG.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
    FILEDIALOG.setWindowTitle("python记事本 - 打开")
    FILEDIALOG.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    sys.exit(app.exec())
