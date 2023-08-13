import datetime

import pyperclip

from widgets import *
import sys
import os
import getpass
import threading

USERNAME = getpass.getuser()


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


def add_cascade(parents: QMenuBar, label='', icon=None):
    return parents.addMenu(label)


def add_command(parents, label='', command=lambda: None, icon=QIcon(), shortcut=''):
    act = QAction(label, parents)
    act.setIcon(icon)
    act.setShortcut(shortcut)
    act.triggered.connect(command)
    return parents.addAction(act)


class MainWindow(QMainWindow):
    """docstring for MainWindow"""
    text: list[TextEdit]
    menu: QMenuBar

    def __init__(self):
        super().__init__()
        self.resize(1300, 700)
        self.setWindowIcon(QIcon(".//icon//notepad.ico"))
        # self.setWindowTitle("python记事本")
        self.menu = self.menuBar()
        self.menu.setStyleSheet("background-color:rgb(255, 255, 255);")
        with open("style.qss") as fo:
            self.setStyleSheet(fo.read())
        self.note = QTabWidget(self)
        self.note.setFont(FONT)
        self.note.resize(950, 580)
        self.note.move(150, 30)
        self.text = []
        get = get_path()
        self.paths = [get]
        # threading.Thread(target=self.add_menu).start()
        self.right = self.note.tabBar().RightSide
        self.start()
        self.add_menu()
        self.note.tabBar().setMovable(True)
        self.show()

    def add_menu(self):
        file = add_cascade(self.menu, "文件(F)")
        add_command(file, label="新建", shortcut="Ctrl+N", command=self.new)
        file.addSeparator()
        add_command(file, label="打开", shortcut="Ctrl+O", command=self.open)
        file.addSeparator()
        add_command(file, label="保存", shortcut="Ctrl+S", command=self._save)
        add_command(file, label="全部保存", command=self._save_all)
        add_command(file, label="另存为", shortcut="Ctrl+Shift+S", command=self._save_as)
        file.addSeparator()
        add_command(file, label="退出", shortcut="Alt+F4", command=QApplication.instance().quit)
        edit = add_cascade(self.menu, "编辑(E)")
        add_command(edit, label="插入当前时间",
                    command=lambda: self.text[self.note.currentIndex()].text.textCursor().insertText(
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        add_command(edit, label="复制",
                    command=lambda: pyperclip.copy(self.text[self.note.currentIndex()].text.textCursor().selectedText()))
        help_ = add_cascade(self.menu, "帮助(H)")
        add_command(help_, label="设置", command=lambda: Setting(self))
        add_command(help_, label="关于",
                    command=lambda: QMessageBox.information(QWidget(), "关于", """python记事本1.0.0
Copyright(2023)"""))
        
    def resizeEvent(self, *args, **kwargs):
        super().resizeEvent(*args, **kwargs)
        self.note.resize(self.width() - 150, self.height())
        for i in self.text:
            i: TextEdit
            i.resize(self.note.width() - int(i.text.lineNumberArea.width() / 5), self.note.height() - 50)

    def open(self):
        path = QFileDialog.getOpenFileNames()
        print(path)
        if path[-1] != "":
            for i in path[0]:
                self.paths.append(i)
                self.start()
            self.note.setCurrentIndex(self.note.count() - 1)

    @staticmethod
    def saves(string):
        if string != f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad_run_c_error.error" \
                and string != "" \
                and string != f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad_chinese_words_for_15.python_notepad":
            with open(f"C:/Users/{USERNAME}/AppData/Local/Temp/python_notepad.tmp", "wt") as fo:
                fo.write(string)
                fo.close()

    def start(self):
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
                    read = ''
        else:
            read = ''
        text = TextEdit(self)
        # text.resize(self.note.width(), self.note.height())
        text.append(read)
        text.text.setFont(FONT)
        self.note.addTab(text, os.path.basename(self.paths[-1]))
        self.text.append(text)
        self.note.tabBar().setTabButton(self.note.count() - 1, self.right, TabButtonWidget())
        self.setWindowTitle(f"python记事本 - {os.path.basename(self.paths[self.note.currentIndex()])}")

    def _save(self):
        index = self.note.currentIndex()
        if os.path.isfile(self.paths[index]):
            with open(self.paths[index], 'wt') as fo:
                fo.write(self.text[index].toText())
        else:
            path = QFileDialog.getSaveFileName()
            if path[-1] != "":
                with open(path[0], 'wt') as fo:
                    fo.write(self.text[index].toText())

    def _save_as(self):
        index = self.note.currentIndex()
        path = QFileDialog.getSaveFileName()
        if path[-1] != "":
            with open(path[0], 'wt') as fo:
                fo.write(self.text[index].toText())

    def _save_all(self):
        for index in range(self.note.count()):
            if os.path.isfile(self.paths[index]):
                with open(self.paths[index], 'wt') as fo:
                    fo.write(self.text[index].toText())
            else:
                path = QFileDialog.getSaveFileName()
                if path[-1] != "":
                    with open(self.paths[index], 'wt') as fo:
                        fo.write(self.text[index].toText())

    def new(self):
        self.paths.append("")
        text = TextEdit(self)
        # text.resize(self.note.width(), self.note.height())
        text.text.setFont(FONT)
        self.note.addTab(text, "无标题")
        self.text.append(text)
        self.note.tabBar().setTabButton(self.note.count() - 1, self.right, TabButtonWidget())
        self.setWindowTitle("python记事本 - 无标题")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
