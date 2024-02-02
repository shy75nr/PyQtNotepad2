
import os
import sys
import threading
import time
from datetime import datetime

import pyperclip
from PyQt5.QtCore import *

from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import *

from constants import *
import translate


# import qrc_resources

class CursorChangeButton(QPushButton):
    def enterEvent(self, a0: QMoveEvent) -> None:
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(a0)


class OutlineButton(CursorChangeButton):
    def moveEvent(self, a0: QMoveEvent) -> None:
        super().moveEvent(a0)
        self.setStyleSheet(OUTLINE.format("255, 255, 255", "0, 0, 0"))

    def enterEvent(self, a0: QMoveEvent) -> None:
        super().enterEvent(a0)
        self.setStyleSheet(OUTLINE.format("50, 93, 136", "255, 255, 255"))

    def leaveEvent(self, a0: QEvent) -> None:
        super().leaveEvent(a0)
        self.setStyleSheet(OUTLINE.format("255, 255, 255", "0, 0, 0"))


class LineNumPaint(QWidget):
    def __init__(self, q_edit, parents=None):
        super().__init__(parents)
        self.q_edit_line_num = q_edit

    def sizeHint(self):
        return QSize(self.q_edit.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.q_edit_line_num.lineNumberAreaPaintEvent(event)


class PlainTextEditWithLineNum(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setLineWrapMode(QPlainTextEdit.NoWrap)  # 不自动换行
        self.lineNumberArea = LineNumPaint(self, parent)
        self.document().blockCountChanged.connect(self.update_line_num_width)
        self.document().cursorPositionChanged.connect(self.highlightCurrentLine)  # 高亮当前行
        self.verticalScrollBar().sliderMoved.connect(self.scroll_event)  # 滚动条移动更新行号
        self.update_line_num_width()
        self.parents = parent

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)
        # if hasattr(self.parents, "parents"):
        try:
            self.parents.parents.file_num.setText(f"  共{len(self.toPlainText())}个字符  ")
        except AttributeError:
            pass

    def goToLine(self, line):
        if isinstance(line, tuple):
            if line[1]:
                line = int(line[0]) - 1
            else:
                return
        tc = self.textCursor()
        position = self.document().findBlockByNumber(line - 1).position()
        tc.setPosition(position, QTextCursor.MoveAnchor)
        self.setTextCursor(tc)

    def goToEnd(self):
        tc = self.textCursor()
        tc.movePosition(QTextCursor.End)
        self.setTextCursor(tc)

    def wheelEvent(self, d: QWheelEvent) -> None:
        self.scroll_event(d)
        super().wheelEvent(d)

    def scroll_event(self, event: QWheelEvent = None):
        self.lineNumberArea.update()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.lineNumberArea.update()
        self.highlightCurrentLine()
        tc = self.textCursor()
        try:
            self.parents.parents.row_column.setText(f"  第{tc.blockNumber() + 1}行,第{tc.columnNumber() + 1}列  ")
        except AttributeError:
            pass

    def update_number(self):
        self.update()
        self.highlightCurrentLine()
        self.lineNumberArea.update()

    def mousePressEvent(self, e: 'QMouseEvent') -> None:
        super().mousePressEvent(e)
        self.update_number()
        tc = self.textCursor()
        try:
            self.parents.parents.row_column.setText(f"  第{tc.blockNumber() + 1}行,第{tc.columnNumber() + 1}列  ")
        except AttributeError:
            pass

    def mouseReleaseEvent(self, e: 'QMouseEvent') -> None:
        super().mouseReleaseEvent(e)
        self.update_number()
        tc = self.textCursor()
        try:
            self.parents.parents.row_column.setText(f"  第{tc.blockNumber() + 1}行,第{tc.columnNumber() + 1}列  ")
        except AttributeError:
            pass

    def lineNumberAreaWidth(self):
        block_count = self.document().blockCount() + 100
        max_value = max(1, block_count)
        d_count = len(str(max_value))
        _width = self.fontMetrics().width('9') * d_count + 5
        return _width

    def update_line_num_width(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        # self.move(self.lineNumberArea.width(),0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            # lineColor = QColor(Qt.blue).lighter(190)
            selection.format.setBackground(QColor(LINECOLOR))
            selection.format.setForeground(QColor(FOREGROUNDLINECOLOR))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        cursor = QTextCursor(self.document())
        painter = QPainter(self.lineNumberArea)
        painter.setFont(FONT_)

        painter.fillRect(event.rect(), QColor(LINENUMBERCOLOR))
        line_height = self.fontMetrics().lineSpacing()  # 包含行间距的行高

        block_number = self.cursorForPosition(QPoint(0, int(line_height / 2))).blockNumber()
        first_visible_block = self.document().findBlock(block_number)
        blockNumber = block_number
        cursor.setPosition(self.cursorForPosition(QPoint(0, int(line_height / 2))).position())
        rect = self.cursorRect()
        scroll_compensation = rect.y() - int(rect.y() / line_height) * line_height
        top = scroll_compensation
        last_block_number = self.cursorForPosition(QPoint(0, self.height() - 1)).blockNumber()

        height = self.fontMetrics().height()
        block = first_visible_block
        # while block.isValid() and (top <= event.rect().bottom()) and blockNumber <= last_block_number:
        rg = self.toPlainText().count("\n") + 1
        rg = rg if rg < 50 else 50
        for x in range(rg):
            # cur_line_count = block.lineCount()
            if block.isVisible():
                number = str(blockNumber + 1)
                painter.setPen(QColor(LINENUMBERFOREGROUNDCOLOR))
                # print((0, top, self.lineNumberArea.width(), height), number)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignCenter, number)
            block = block.next()
            top = top + line_height
            blockNumber += 1


class TextEdit(QFrame):
    def __init__(self, parents: QMainWindow):
        super().__init__(parents)
        self.parents = parents
        self.text = PlainTextEditWithLineNum(self)
        # self.text.resize(self.width(), self.height())
        self.text.resize(self.parents.width() - 150, self.parents.height() - 70)
        self.text.move(int(self.text.lineNumberArea.width() / 5), 0)
        self.text.setFrameShape(QFrame.NoFrame)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # act=QSlider()
        # act.triggered.connect(self.text.update_number)
        # self.text.verticalScrollBar().triggerAction(act)
        # self.setFrameShape(QFrame.Box)
        # self.set
        # self.setLineWidth(0)
        self.text.setTabStopWidth(4 * QFontMetrics(self.text.font()).width(' '))
        self.append = self.text.append
        self.setText = self.text.setText
        self.toText = self.text.toPlainText
        self.textCursor = self.text.textCursor
        self.clear = self.text.clear
        self.find = self.text.find

        # self.text.horizontalScrollBar().hide()
        stp = QScrollBar(self)
        stp.resize(20, self.text.height() - 25)
        stp.move(self.text.width() - 25, 0)
        self.text.setHorizontalScrollBar(stp)
        self.setAcceptDrops(True)
        stp.show()

    def dragEnterEvent(self, e):
        pass

    def resize(self, *__args):
        super().resize(*__args)
        self.text.resize(*__args)


class PhotoEdit(QScrollArea):
    def __init__(self, parents, path):
        super().__init__(parents)
        self.parents = parents
        self.setFrameShape(QFrame.NoFrame)
        img = QImage(path)
        self.text = QPlainTextEdit(self)
        self.text.resize(0, 0)
        self.text.hide()
        rect = img.rect()
        self.w = rect.width()
        self.h = rect.height()
        size = QLabel(f"{path}\t{self.w}x{self.h}", self)
        size.setFont(FONT_)
        self.large = QLabel("100%", self)
        self.large.setFont(FONT_)
        self.large.move(500, 0)
        self.sp = QSlider(Qt.Horizontal, self)
        self.sp.move(545, 0)
        self.sp.resize(500, 20)
        self.sp.setRange(10, 800)
        self.sp.setValue(100)
        self.sp.valueChanged[int].connect(self.change)
        # size.resize(20,1000)
        self.image = QLabel("", self)
        self.image.setPixmap(QPixmap(path))
        self.image.move(0, 20)
        self.image.setScaledContents(True)
        self.append = self.text.appendPlainText
        self.setText = self.text.setPlainText
        self.toText = self.text.toPlainText
        self.textCursor = self.text.textCursor
        self.clear = self.text.clear
        self.find = self.text.find
        self.goToLine = lambda f=0: None
        self.text.goToEnd = lambda f=0: None
        self.text.goToLine = lambda f=0: None

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Left:
            self.sp.setValue(self.sp.value() - 1)
        elif a0.key() == Qt.Key_Right:
            self.sp.setValue(self.sp.value() + 1)
        super().keyPressEvent(a0)

    def change(self, e):
        self.large.setText(f"{e}%")
        self.image.resize(int(self.w * e / 100), int(self.h * e / 100))


class AudioPlayer(QFrame):
    def __init__(self, parents, path):
        super().__init__(parents)
        self.sp = QSlider(Qt.Horizontal, self)
        self.sp.resize(parents.width() - 350, 20)
        self.sp.move(50, 30)
        self.start = QLabel("00:00", self)
        self.end = QLabel("00:00", self)
        self.playing = False
        self.start.move(0, 28)
        self.start.setFont(FONT_)
        self.end.move(self.start.width() + self.sp.width() - 30, 28)
        self.end.setFont(FONT_)
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.sp.setMinimum(0)
        self.end.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        self.volume = QSlider(Qt.Horizontal, self)
        self.volume.move(50, 60)
        self.volume.setRange(0, 100)
        self.lb = QLabel("100", self)
        self.lb.setFont(FONT_)
        self.lb.move(150, 60)
        self.volume.valueChanged[int].connect(lambda f: self.player.setVolume(f) or self.lb.setText(str(f)))
        self.sp.sliderMoved[int].connect(lambda: self.changePosition())
        self.volume.setValue(100)
        lb = QLabel("音量", self)
        lb.setFont(FONT_)
        lb.move(0, 60)
        lb = QLabel(f"{path}", self)
        lb.setFont(FONT_)
        t = QTimer(self)
        t.setInterval(1000)
        t.timeout.connect(self.flush)
        t.start()
        play = QPushButton("开始", self)
        play.move(0, 90)
        play.setFont(FONT_)
        play.clicked.connect(self.starts)
        stop = QPushButton("暂停", self)
        stop.move(80, 90)
        stop.setFont(FONT_)
        stop.clicked.connect(self.pause)
        self.text = QPlainTextEdit(self)
        self.text.resize(0, 0)
        self.text.hide()

        self.append = self.text.appendPlainText
        self.setText = self.text.setPlainText
        self.toText = self.text.toPlainText
        self.textCursor = self.text.textCursor
        self.clear = self.text.clear
        self.find = self.text.find
        self.goToLine = lambda f=0: None
        self.text.goToEnd = lambda f=0: None
        self.text.goToLine = lambda f=0: None
        self.show()

    def changePosition(self):
        self.pause()
        self.player.setPosition(self.sp.value())
        self.flush()
        self.starts()

    def starts(self):
        self.playing = True
        self.player.play()

    def pause(self):
        self.playing = False
        self.player.pause()

    def flush(self):
        if self.playing:
            self.sp.setValue(self.sp.value() + 1000)
            if self.sp.value() >= self.sp.maximum():
                self.sp.setValue(0)
        self.start.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.end.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        self.sp.setMaximum(self.player.duration())


class MediaPlayer(QFrame):
    def __init__(self, parents, path):
        super().__init__(parents)
        self.parents = parents
        self.sp = QSlider(Qt.Horizontal, self)
        self.start = QLabel("00:00", self)
        self.end = QLabel("00:00", self)
        self.playing = False
        self.start.setFont(FONT_)
        self.end.setFont(FONT_)
        self.player = QMediaPlayer()
        self.video = QVideoWidget(self)
        self.video.show()
        self.player.setVideoOutput(self.video)
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.video.move(0, 30)
        self.end.move(self.start.width() + self.sp.width() - 30, self.video.height() + 38)
        self.sp.setMinimum(0)
        self.end.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        self.video.setStyleSheet("background-color:#FFFFFF")
        self.volume = QSlider(Qt.Horizontal, self)
        self.volume.setRange(0, 100)
        self.lb = QLabel("100", self)
        self.lb.setFont(FONT_)
        self.starts()
        self.pause()
        self.volume.valueChanged[int].connect(lambda f: self.player.setVolume(f) or self.lb.setText(str(f)))
        self.sp.sliderMoved[int].connect(lambda: self.changePosition())
        self.player.setPosition(self.sp.value())
        self.flush()
        self.volume.setValue(100)
        self.lb2 = QLabel("音量", self)
        self.lb2.setFont(FONT_)
        lb = QLabel(f"{path}", self)
        lb.setFont(FONT_)
        t = QTimer(self)
        t.setInterval(1000)
        t.timeout.connect(self.flush)
        t.start()
        self.play = QPushButton("开始", self)
        self.play.setFont(FONT_)
        self.play.clicked.connect(self.starts)
        self.stop = QPushButton("暂停", self)
        self.stop.setFont(FONT_)
        self.stop.clicked.connect(self.pause)
        self.text = QPlainTextEdit(self)
        self.text.resize(0, 0)
        self.text.hide()

        self.append = self.text.appendPlainText
        self.setText = self.text.setPlainText
        self.toText = self.text.toPlainText
        self.textCursor = self.text.textCursor
        self.clear = self.text.clear
        self.find = self.text.find
        self.goToLine = lambda f=0: None
        self.text.goToEnd = lambda f=0: None
        self.text.goToLine = lambda f=0: None
        self.show()

    def changePosition(self):
        self.pause()
        self.player.setPosition(self.sp.value())
        self.flush()
        self.starts()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.sp.resize(self.parents.width() - 260, 20)
        self.video.resize(self.parents.width(), self.parents.height() - 210)
        h = self.video.height()
        self.sp.move(50, h + 40)
        self.start.move(0, h + 38)
        self.end.move(self.sp.x() + self.sp.width() + 10, h + 38)
        self.volume.move(50, h + 60)
        self.lb.move(150, h + 60)
        self.lb2.move(0, h + 60)
        self.play.move(0, h + 90)
        self.stop.move(80, h + 90)

    def starts(self):
        self.playing = True
        self.player.play()

    def pause(self):
        self.playing = False
        self.player.pause()

    def flush(self):
        if self.playing:
            self.sp.setValue(self.sp.value() + 1000)
            if self.sp.value() >= self.sp.maximum():
                self.sp.setValue(0)
        self.start.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.end.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        self.sp.setMaximum(self.player.duration())


class TabButtonWidget(QWidget):

    def __init__(self, parents=None, index=0):
        super(TabButtonWidget, self).__init__()
        self.index = index
        # Create button's
        self.button_add = CursorChangeButton("  ×", self)
        self.button_add.setFont(FONT_)
        self.button_add.setStyleSheet("background-color:rgba(0, 0, 0, 0)")
        # Set button size
        self.button_add.setFixedSize(30, 30)
        self.button_add.clicked.connect(lambda: parents.close_tab(self.index))
        # Create layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Add button's to layout
        self.layout.addWidget(self.button_add)
        # Use layout in widget
        self.setLayout(self.layout)


class FileStatistic(QDialog):
    def __init__(self, paths):
        super().__init__()
        self.resize(980, 70 + len(paths) * 30)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle("python记事本 - 文件统计")
        self.table = QTableWidget(len(paths) + 1, 8, self)
        self.table.resize(self.width(), self.height())
        self.setStyleSheet(WIDGET_STYLE_SHEET)
        self.set(paths)
        self.exec()

    def set(self, paths):
        for i in range(5, 8):
            self.table.setColumnWidth(i, 140)
        self.table.setItem(0, 0, QTableWidgetItem(QIcon(""), "文件名", 0))
        self.table.setItem(0, 1, QTableWidgetItem(QIcon(""), "文件类型", 0))
        self.table.setItem(0, 2, QTableWidgetItem(QIcon(""), "文件大小", 0))
        self.table.setItem(0, 3, QTableWidgetItem(QIcon(""), "文件行数", 0))
        self.table.setItem(0, 4, QTableWidgetItem(QIcon(""), "文件长度", 0))
        self.table.setItem(0, 5, QTableWidgetItem(QIcon(""), "创建日期", 0))
        self.table.setItem(0, 6, QTableWidgetItem(QIcon(""), "访问日期", 0))
        self.table.setItem(0, 7, QTableWidgetItem(QIcon(""), "修改日期", 0))
        for i in range(len(paths)):
            print(paths[i], i + 1)
            self.table.setItem(i + 1, 0, QTableWidgetItem(QIcon(".\\icon\\python.gif"), os.path.basename(paths[i]), 0))
            self.table.setItem(i + 1, 1, QTableWidgetItem(QIcon(""), os.path.splitext(paths[i])[-1], 0))
            self.table.setItem(i + 1, 2,
                               QTableWidgetItem(QIcon(""), str(round(os.path.getsize(paths[i]) / 1024, 2)) + "KB", 0))
            is_open = False
            try:
                with open(paths[i], 'rt', encoding="GBK") as fo:
                    read = fo.read()
                    is_open = True
            except (UnicodeError, UnicodeDecodeError):
                try:
                    with open(paths[i], 'rt', encoding="UTF-8") as fo:
                        read = fo.read()
                        is_open = True
                except(UnicodeError, UnicodeDecodeError):
                    is_open = False
            t = os.stat(paths[i])
            if is_open:
                self.table.setItem(i + 1, 3, QTableWidgetItem(QIcon(""), str(read.count("\n")), 0))
                self.table.setItem(i + 1, 4, QTableWidgetItem(QIcon(""), str(len(read)), 0))
            self.table.setItem(i + 1, 5, QTableWidgetItem(QIcon(""), str(datetime.fromtimestamp(t.st_ctime)), 0))
            self.table.setItem(i + 1, 6, QTableWidgetItem(QIcon(""), str(datetime.fromtimestamp(t.st_atime)), 0))
            self.table.setItem(i + 1, 7, QTableWidgetItem(QIcon(""), str(datetime.fromtimestamp(t.st_mtime)), 0))

    def resizeEvent(self, a0: QResizeEvent) -> None:
        super().resizeEvent(a0)
        self.table.resize(self.width(), self.height())


class ShowTextDialog(QDialog):
    def __init__(self, title: str, string: str):
        super().__init__()
        self.setStyleSheet(WIDGET_STYLE_SHEET)
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setWindowTitle(title)
        self.setStyleSheet(WIDGET_STYLE_SHEET)
        self.text = PlainTextEditWithLineNum(self)
        self.text.resize(500, 400)
        self.text.setFont(FONT)
        self.text.append(string)
        self.text.move(int(self.text.lineNumberArea.width() / 5), 0)
        self.text.setFrameShape(QFrame.NoFrame)
        self.text.goToLine(1)
        self.exec()

    def setDisabled(self, a0: bool) -> None:
        super().setDisabled(a0)
        self.text.setDisabled(a0)


class FileTreeWidget(QFrame):

    def __init__(self, parents):
        super().__init__(parents)
        self.parents = parents
        self.initUI()

    def initUI(self):
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir(os.path.dirname(self.parents.paths[0])).rootPath())
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(os.path.dirname(self.parents.paths[0])))
        self.tree.setAnimated(False)
        self.tree.setIndentation(10)
        self.tree.setSortingEnabled(True)
        self.tree.setFrameShape(QFrame.NoFrame)
        font = FONT_
        font.setPointSize(9)
        self.tree.setFont(font)
        font.setPointSize(12)
        self.tree.resize(self.width(), self.height())
        self.setFrameShape(QFrame.NoFrame)
        # print(self.tree)
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.tree.doubleClicked.connect(self.file_name)
        self.setLayout(windowLayout)
        self.show()

    # def set_dir(self, dir):
    #     self.model = QFileSystemModel()
    #     self.model.setRootPath(QDir(dir).rootPath())
    #     self.tree = QTreeView(self)
    #     self.tree.setModel(self.model)
    #     self.tree.setRootIndex(self.model.index(dir))
    #     self.tree.setAnimated(False)
    #     self.tree.setIndentation(10)
    #     self.tree.setSortingEnabled(True)
    #     self.tree.setFrameShape(QFrame.NoFrame)
    #     font = FONT_
    #     font.setPointSize(9)
    #     self.tree.setFont(font)
    #     font.setPointSize(12)
    #     self.tree.resize(self.width(), self.height())
    #     self.setFrameShape(QFrame.NoFrame)
    #     # print(self.tree)
    #     windowLayout = QVBoxLayout()
    #     windowLayout.addWidget(self.tree)
    #     self.tree.doubleClicked.connect(self.file_name)
    #     self.setLayout(windowLayout)

    def file_name(self, model_index: QModelIndex):
        # print(self.model.filePath(model_index))  # 输出文件的地址。
        # print(self.model.fileName(model_index))  # 输出文件名
        file = self.model.filePath(model_index)
        if os.path.isfile(file) and file not in self.parents.paths:
            self.parents.paths.append(self.model.filePath(model_index))
            self.parents.start()


class ShowAbout(QDialog):
    def __init__(self):
        super().__init__()
        string = """PyQt5 - Comprehensive Python Bindings for Qt v5
===============================================
https://pypi.org/project/PyQt5/
===============================================
Qt is set of cross-platform C++ libraries that implement high-level APIs for accessing many aspects of modern desktop
and mobile systems.  These include location and positioning services, multimedia, NFC and Bluetooth connectivity, a
Chromium based web browser, as well as traditional UI development.
PyQt5 is a comprehensive set of Python bindings for Qt v5.  It is implemented as more than 35 extension modules and
enables Python to be used as an alternative application development language to C++ on all supported platforms including
iOS and Android.
PyQt5 may also be embedded in C++ based applications to allow users of thoseapplications to configure or enhance the
functionality of those applications.

Author
PyQt5 is copyright (c) Riverbank Computing Limited.  Its homepage is https://www.riverbankcomputing.com/software/pyqt/.
Support may be obtained from the PyQt mailing list at https://www.riverbankcomputing.com/mailman/listinfo/pyqt/.

License
PyQt5 is released under the GPL v3 license and under a commercial license that allows for the development of proprietary
applications.

Documentation
The documentation for the latest release can be found `here <https://www.riverbankcomputing.com/static/Docs/PyQt5/>`__.

Installation
The GPL version of PyQt5 can be installed from PyPI::
    pip install PyQt5
``pip`` will also build and install the bindings from the sdist package but Qt's ``qmake`` tool must be on ``PATH``.
The ``sip-install`` tool will also install the bindings from the sdist package but will allow you to configure many
aspects of the installation.
"""
        self.resize(880, 640)
        self.setWindowTitle("关于PyQt")
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.setStyleSheet("background-color:white;")
        lb = QLabel("About PyQt", self)
        lb.move(100, 0)
        ft = QFont("Microsoft YaHei UI", 13)
        ft.setBold(True)
        lb.setFont(ft)
        lb2 = QLabel(string, self)
        lb2.move(100, 30)
        lb2.setFont(QFont("Microsoft YaHei UI", 10))
        img = QLabel("", self)
        img.setPixmap(QPixmap(".\\icon\\about.png"))
        img.move(20, 20)
        exit_ = OutlineButton("确定", self)
        exit_.move(780, 605)
        exit_.clicked.connect(self.close)
        exit_.setFont(QFont("Microsoft YaHei UI", 10))
        self.exec()


class Translation(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(660, 210)
        self.setWindowIcon(QIcon(".//icon//notepad.ico"))
        self.setWindowTitle("python记事本 - 翻译")
        self.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.from_lang = 'Chinese'
        self.to_lang = 'English'
        self.lg = ("Chinese", "English")
        self.translate = translate.Translator(from_lang=self.from_lang, to_lang=self.to_lang)
        language = ("中文(简体)", "English")
        l = QLabel("从", self)
        l.setFont(FONT)
        l = QLabel("翻译到", self)
        l.setFont(FONT)
        l.move(300, 0)
        bx1 = QComboBox(self)
        bx1.move(30, 0)
        bx1.resize(200, 25)
        style = """    border-radius:3px;
    border:2px solid rgb(50, 93, 136);
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);"""
        bx1.setStyleSheet(style)
        bx1.setFont(FONT)
        bx1.activated[int].connect(self.set_1)
        for i in language:
            bx1.addItem(i)
        bx2 = QComboBox(self)
        bx2.move(360, 0)
        bx2.resize(200, 25)
        bx2.setStyleSheet(style)
        bx2.setFont(FONT)
        bx2.activated[int].connect(self.set_2)
        for i in language:
            bx2.addItem(i)
        bx2.setCurrentIndex(1)
        btn = CursorChangeButton("", self)
        btn.setIcon(QIcon(".\\icon\\translate.png"))
        btn.setStyleSheet("""border-radius:20px;
    border:1px solid rgb(140, 140, 140);
    font-family:Microsoft YaHei UI;""")
        btn.clicked.connect(self.run)
        btn.resize(38, 38)
        btn.move(295, 90)
        self.text1 = QTextEdit(self)
        self.text1.resize(275, 170)
        self.text1.setFont(FONT)
        self.text1.move(5, 40)
        self.text2 = QTextEdit(self)
        self.text2.resize(275, 170)
        self.text2.setFont(FONT)
        self.text2.move(345, 40)
        self.exec()

    def set_1(self, i):
        self.from_lang = self.lg[i]
        self.translate = translate.Translator(from_lang=self.from_lang, to_lang=self.to_lang)

    def set_2(self, i):
        self.to_lang = self.lg[i]
        self.translate = translate.Translator(from_lang=self.from_lang, to_lang=self.to_lang)

    def run(self):
        self.text2.setText("● ● ●")
        QApplication.processEvents()
        try:
            self.text2.setText(self.translate.translate(self.text1.toPlainText()))
        except RuntimeError:
            self.text2.setText("翻译失败")


class ToolTip(QFrame):
    def btn(self, icon, w, h, x, y, text=""):
        b = CursorChangeButton("", self)
        b.resize(w, h)
        b.setIcon(QIcon(icon))
        b.setIconSize(QSize(w, h))
        b.move(x, y)
        b.setStyleSheet("background-color:rgba(255,255,255,0);")
        b.setToolTip(text)
        return b

    def __init__(self, parents):
        super().__init__(parent=parents)
        # self.resize(37, parents.height())
        self.setStyleSheet("background-color:#FFFFFF;")
        new = self.btn(".\\icon\\new-file.png", 36, 37, 0, 0, "新建")
        new.clicked.connect(parents.new)
        open = self.btn(".\\icon\\open.png", 32, 32, 2, 42, "打开")
        open.clicked.connect(lambda: threading.Thread(target=parents.open).start())
        save = self.btn(".\\icon\\save.png", 36, 37, 0, 80, "保存")
        save.clicked.connect(parents._save)
        copy = self.btn(".\\icon\\document-copy.png", 34, 34, 0, 120, "复制")
        copy.clicked.connect(lambda: pyperclip.copy(
            parents.text[parents.note.currentIndex()].text.textCursor().selectedText()))
        cut = self.btn(".\\icon\\scissors.png", 36, 36, 0, 160, "剪切")
        cut.clicked.connect(parents.cut)
        paste = self.btn(".\\icon\\paste.png", 35, 35, 0, 200, "粘贴")
        paste.clicked.connect(
            lambda: parents.text[parents.note.currentIndex()].text.textCursor().insertText(pyperclip.paste()))
        find = self.btn(".\\icon\\find.png", 36, 37, 0, 240, "查找")
        find.clicked.connect(parents.Find_UI)
        replace = self.btn(".\\icon\\replace-color.png", 36, 37, 0, 280, "替换")
        replace.clicked.connect(parents.Replace_UI)
        undo = self.btn(".\\icon\\undo.png", 36, 37, 0, 320, "撤销")
        undo.clicked.connect(lambda: parents.text[parents.note.currentIndex()].text.undo())
        redo = self.btn(".\\icon\\redo.png", 36, 37, 0, 360, "重做")
        redo.clicked.connect(lambda: parents.text[parents.note.currentIndex()].text.redo())
        help_ = self.btn(".\\icon\\help.ico", 36, 37, 0, 400, "关于")
        help_.clicked.connect(lambda: ShowTextDialog("python快乐记事本 更新日志", ABOUT).setDisabled(False))
        exit_ = self.btn(".\\icon\\exit.png", 32, 32, 0, 440, "退出")
        exit_.clicked.connect(QApplication.instance().quit)
        # new.move(0)


class OpacityChangeWindow(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标签背景色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(141, 91, 153))
        # 设置透明度
        self.opacity = QGraphicsOpacityEffect()  # 透明度对象
        self.opacity.setOpacity(0)  # 初始化设置透明度为0，即完全透明
        self.setGraphicsEffect(self.opacity)  # 把标签的透明度设置为为self.opacity

        self.draw()  # 淡入效果开始

    def draw(self):
        self.opacity.i = 1  # 用于记录透明度变化与循环次数

        def timeout():  # 超时函数：改变透明度
            self.opacity.setOpacity(self.opacity.i / 100)
            self.setGraphicsEffect(self.opacity)  # 改变标签透明度
            self.opacity.i += 5
            if self.opacity.i >= 100:  # 此时透明度为1，即不透明，控件已经完全显示出来了
                self.timer.stop()  # 计时器停止
                self.timer.deleteLater()

        self.timer = QTimer()  # 计时器
        self.timer.setInterval(3)  # 设置间隔时间，毫秒为单位
        self.timer.timeout.connect(timeout)  # 超时槽函数，每到达间隔时间，调用该函数
        self.timer.start()  # 计时器开始

    def un_draw(self):
        self.opacity.i = 100  # 用于记录透明度变化与循环次数

        def timeout():  # 超时函数：改变透明度
            self.opacity.setOpacity(self.opacity.i / 100)
            self.setGraphicsEffect(self.opacity)  # 改变标签透明度
            self.opacity.i -= 5
            if self.opacity.i <= 0:  # 此时透明度为1，即不透明，控件已经完全显示出来了
                self.timer.stop()  # 计时器停止
                self.hide()
                self.timer.deleteLater()

        self.timer = QTimer()  # 计时器
        self.timer.setInterval(3)  # 设置间隔时间，毫秒为单位
        self.timer.timeout.connect(timeout)  # 超时槽函数，每到达间隔时间，调用该函数
        self.timer.start()  # 计时器开始


class Setting(OpacityChangeWindow):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parents: QMainWindow, test=False):
        super().__init__(parents)
        self.test = test
        parents.setWindowTitle("python记事本 - 设置")
        self.parents = parents
        self.setFrameShape(QFrame.NoFrame)
        self.resize(1920, 1080)
        self.setStyleSheet("background-color:rgba(255, 255, 255, 1)")
        exit_ = CursorChangeButton("←", self)
        font = QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setBold(True)
        font.setPointSize(12)
        exit_.setFont(font)
        font.setPointSize(30)
        exit_.resize(60, 60)
        exit_.move(0, 20)
        exit_.setStyleSheet("background-color:rgba(0, 0, 0, 0)")
        exit_.clicked.connect(self.exit)
        icon = QLabel('', self)
        icon.setPixmap(QPixmap(".\\icon\\notepad.ico"))
        icon.move(50, 35)
        icon.resize(40, 40)
        icon.setScaledContents(True)
        lb = QLabel("python记事本 - 设置", self)
        lb.setFont(font)
        lb.move(100, 20)
        self.ft = QLabel(
            f'字体: {FONT.family()}   大小: {FONT.pointSize()}   重量: {"较重" if FONT.bold() else "正常"} '
            f'下划线: {"有" if FONT.underline() else "无"} 删除线: {"有" if FONT.overline() else "无"}', self)
        self.ft.setFont(FONT_)
        self.ft.move(100, 100)
        self.ft.resize(1000, 30)
        change_font = OutlineButton("更改字体", self)
        change_font.setFont(FONT_)
        change_font.move(950, 100)
        change_font.clicked.connect(self.change_font)
        change_font.setStyleSheet(STYLE_SHEET)
        change_font.resize(100, 25)
        self._line_color = QLabel(f"行高亮颜色: {LINECOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._line_color.move(100, 140)
        self._line_color.setFont(FONT_)
        self._line_color.resize(280, 30)
        self.line_color = QLabel("████████████████████████████", self)
        self.line_color.move(380, 140)
        self.line_color.setStyleSheet(f"color: {LINECOLOR};")
        self.line_color.setFont(FONT_)
        change_line_color = OutlineButton("更改颜色", self)
        change_line_color.setFont(FONT_)
        change_line_color.move(950, 140)
        change_line_color.clicked.connect(self.change_line_color)
        change_line_color.setStyleSheet(STYLE_SHEET)
        change_line_color.resize(100, 25)
        self._foreground_line_color = QLabel(f"行高亮前景色: {FOREGROUNDLINECOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_line_color.move(100, 180)
        self._foreground_line_color.setFont(FONT_)
        self._foreground_line_color.resize(280, 30)
        self.foreground_line_color = QLabel("████████████████████████████", self)
        self.foreground_line_color.move(380, 180)
        self.foreground_line_color.setStyleSheet(f"color: {FOREGROUNDLINECOLOR};")
        self.foreground_line_color.setFont(FONT_)
        change_foreground_line_color = OutlineButton("更改颜色", self)
        change_foreground_line_color.setFont(FONT_)
        change_foreground_line_color.move(950, 180)
        change_foreground_line_color.clicked.connect(self.change_foreground_line_color)
        change_foreground_line_color.setStyleSheet(STYLE_SHEET)
        change_foreground_line_color.resize(100, 25)
        self._foreground_selection_line_color = QLabel(f"被选择前景色: {SELECTIONFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_selection_line_color.move(100, 260)
        self._foreground_selection_line_color.setFont(FONT_)
        self._foreground_selection_line_color.resize(280, 30)
        self.foreground_selection_line_color = QLabel("████████████████████████████", self)
        self.foreground_selection_line_color.move(380, 260)
        self.foreground_selection_line_color.setStyleSheet(f"color: {SELECTIONFOREGROUNDCOLOR};")
        self.foreground_selection_line_color.setFont(FONT_)
        change_foreground_selection_line_color = OutlineButton("更改颜色", self)
        change_foreground_selection_line_color.setFont(FONT_)
        change_foreground_selection_line_color.move(950, 260)
        change_foreground_selection_line_color.clicked.connect(self.change_foreground_selection_line_color)
        change_foreground_selection_line_color.setStyleSheet(STYLE_SHEET)
        change_foreground_selection_line_color.resize(100, 25)
        self._selection_line_color = QLabel(f"被选择颜色: {SELECTIONCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._selection_line_color.move(100, 220)
        self._selection_line_color.setFont(FONT_)
        self._selection_line_color.resize(240, 30)
        self.selection_line_color = QLabel("████████████████████████████", self)
        self.selection_line_color.move(380, 220)
        self.selection_line_color.setStyleSheet(f"color: {SELECTIONCOLOR};")
        self.selection_line_color.setFont(FONT_)
        change_selection_line_color = OutlineButton("更改颜色", self)
        change_selection_line_color.setFont(FONT_)
        change_selection_line_color.move(950, 220)
        change_selection_line_color.clicked.connect(self.change_selection_line_color)
        change_selection_line_color.setStyleSheet(STYLE_SHEET)
        change_selection_line_color.resize(100, 25)
        self._linenumber_color = QLabel(f"行号颜色: {LINENUMBERCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._linenumber_color.move(100, 300)
        self._linenumber_color.setFont(FONT_)
        self._linenumber_color.resize(280, 30)
        self.linenumber_color = QLabel("████████████████████████████", self)
        self.linenumber_color.move(380, 300)
        self.linenumber_color.setStyleSheet(f"color: {LINENUMBERCOLOR};")
        self.linenumber_color.setFont(FONT_)
        change_linenumber_color = OutlineButton("更改颜色", self)
        change_linenumber_color.setFont(FONT_)
        change_linenumber_color.move(950, 300)
        change_linenumber_color.clicked.connect(self.change_linenumber_color)
        change_linenumber_color.setStyleSheet(STYLE_SHEET)
        change_linenumber_color.resize(100, 25)
        self._foreground_linenumber_color = QLabel(f"行号前景色: {LINENUMBERFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_linenumber_color.move(100, 340)
        self._foreground_linenumber_color.setFont(FONT_)
        self._foreground_linenumber_color.resize(280, 30)
        self.foreground_linenumber_color = QLabel("████████████████████████████", self)
        self.foreground_linenumber_color.move(380, 340)
        self.foreground_linenumber_color.setStyleSheet(f"color: {LINENUMBERFOREGROUNDCOLOR};")
        self.foreground_linenumber_color.setFont(FONT_)
        change_foreground_linenumber_color = OutlineButton("更改颜色", self)
        change_foreground_linenumber_color.setFont(FONT_)
        change_foreground_linenumber_color.move(950, 340)
        change_foreground_linenumber_color.clicked.connect(self.change_foreground_linenumber_color)
        change_foreground_linenumber_color.setStyleSheet(STYLE_SHEET)
        change_foreground_linenumber_color.resize(100, 25)
        self._text_color = QLabel(f"文本框颜色: {TEXTCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._text_color.move(100, 380)
        self._text_color.setFont(FONT_)
        self._text_color.resize(280, 30)
        self.text_color = QLabel("████████████████████████████", self)
        self.text_color.move(380, 380)
        self.text_color.setStyleSheet(f"color: {TEXTCOLOR};")
        self.text_color.setFont(FONT_)
        change_text_color = OutlineButton("更改颜色", self)
        change_text_color.setFont(FONT_)
        change_text_color.move(950, 380)
        change_text_color.clicked.connect(self.change_text_color)
        change_text_color.setStyleSheet(STYLE_SHEET)
        change_text_color.resize(100, 25)
        self._foreground_text_color = QLabel(f"文本框前景色: {TEXTFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_text_color.move(100, 420)
        self._foreground_text_color.setFont(FONT_)
        self._foreground_text_color.resize(280, 30)
        self.foreground_text_color = QLabel("████████████████████████████", self)
        self.foreground_text_color.move(380, 420)
        self.foreground_text_color.setStyleSheet(f"color: {TEXTFOREGROUNDCOLOR};")
        self.foreground_text_color.setFont(FONT_)
        change_foreground_text_color = OutlineButton("更改颜色", self)
        change_foreground_text_color.setFont(FONT_)
        change_foreground_text_color.move(950, 420)
        change_foreground_text_color.clicked.connect(self.change_foreground_text_color)
        change_foreground_text_color.setStyleSheet(STYLE_SHEET)
        change_foreground_text_color.resize(100, 25)
        change_last_font_size_label = QLabel("缩放最小字体:", self)
        change_last_font_size_label.move(100, 460)
        change_last_font_size_label.setFont(FONT_)
        self.change_last_font_size = QLineEdit(self)
        self.change_last_font_size.setText(str(LAST_FONT_SIZE))
        self.change_last_font_size.move(210, 457)
        self.change_last_font_size.setStyleSheet("""border-radius:3px;
    border:2px solid rgb(50, 93, 136);
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")
        self.change_last_font_size.setFont(FONT)
        self.change_last_font_size.textChanged.connect(self.set_last_font_size)
        self.wrap_or_not = QCheckBox("自动换行", self)
        self.wrap_or_not.setFont(FONT_)
        self.wrap_or_not.clicked.connect(self.set_wrap_or_not)
        self.wrap_or_not.move(380, 460)
        self.wrap_or_not.setChecked(WRAP)
        # self.wrap_or_not.setStyleSheet("border:2px solid rgb(151, 198, 235);")
        opacity_label = QLabel("透明度", self)
        opacity_label.move(100, 498)
        opacity_label.setFont(FONT_)
        opacity_num_label = QLabel("0", self)
        opacity_num_label.move(600, 498)
        opacity_num_label.setFont(FONT_)
        opacity_num_label.resize(50, 20)
        opacity_slider = QSlider(Qt.Horizontal, self)
        opacity_slider.move(150, 500)
        opacity_slider.resize(445, 20)
        opacity_slider.setRange(0, 99)
        # opacity_slider.setValue(100)
        opacity_slider.valueChanged[int].connect(
            lambda f=0: opacity_num_label.setText(str(f)) or self.set_opacity(
                1 - f / 100) or opacity_slider.setWindowOpacity(0))
        web_label = QLabel("搜索引擎: ", self)
        web_label.setFont(FONT_)
        web_label.move(100, 540)
        self.web_edit = QLineEdit(self)
        self.web_edit.setFont(FONT_)
        self.web_edit.resize(400, 25)
        self.web_edit.move(180, 540)
        self.web_edit.setText(WEB)
        self.web_edit.setStyleSheet("""border-radius:3px;
    border:2px solid rgb(50, 93, 136);
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")
        self.web_edit.textChanged[str].connect(self.setWeb)
        save = OutlineButton("保存", self)
        save.clicked.connect(self.save)
        save.setFont(FONT_)
        save.move(1060, 100)
        save.resize(100, 25)
        save.setStyleSheet(STYLE_SHEET)
        exits_ = OutlineButton("退出", self)
        exits_.clicked.connect(self.exit)
        exits_.setFont(FONT_)
        exits_.move(1060, 140)
        exits_.resize(100, 25)
        exits_.setStyleSheet(STYLE_SHEET)
        # change_linenumber_color = OutlineButton("更改颜色", self)
        # change_linenumber_color.setFont(FONT_)
        # change_linenumber_color.move(950, 300)
        # change_linenumber_color.clicked.connect(self.change_linenumber_color)
        # change_linenumber_color.setStyleSheet(STYLE_SHEET)
        # change_linenumber_color.resize(100, 25)
        self.show()

    def save(self):
        x = {'linecolor': LINECOLOR, 'fglinecolor': FOREGROUNDLINECOLOR, 'selectioncolor': SELECTIONCOLOR,
             'selectionfgcolor': SELECTIONFOREGROUNDCOLOR, "linenumcolor": LINENUMBERCOLOR,
             'linenumfgcolor': LINENUMBERFOREGROUNDCOLOR, 'textcolor': TEXTCOLOR, 'textfgcolor': TEXTFOREGROUNDCOLOR,
             'web': WEB, 'lastfontsize': LAST_FONT_SIZE, 'wrap': WRAP}
        with open(".\\style\\settings.json", "wt") as fo:
            fo.write(json.dumps(x))

    def setWeb(self):
        global WEB
        WEB = self.web_edit.text()

    def set_opacity(self, f):
        self.parents.setWindowOpacity(f)
        self.parents.note.setWindowOpacity(f)
        self.parents.file_area.setWindowOpacity(f)
        self.parents.dir.setWindowOpacity(f)

    def set_wrap_or_not(self):
        global WRAP
        for i in self.parents.text:
            # i: TextEdit
            i.text.setWordWrapMode(QTextOption.WrapAnywhere if self.wrap_or_not.isChecked() else QTextOption.NoWrap)
            i.text.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOn if self.wrap_or_not.isChecked() else Qt.ScrollBarAlwaysOff)
            WRAP = self.wrap_or_not.isChecked()

    def set_last_font_size(self, e=None):
        global LAST_FONT_SIZE
        try:
            LAST_FONT_SIZE = int(self.change_last_font_size.text())
            self.change_last_font_size.setStyleSheet("""border:2px solid rgb(50, 93, 136);
    border-radius:3px;
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")
        except ValueError:
            if self.change_last_font_size.text() != "":
                self.change_last_font_size.setStyleSheet("""border:2px solid #FF0000;
    border-radius:3px;
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")
            else:
                self.change_last_font_size.setStyleSheet("""border:2px solid rgb(50, 93, 136);
    border-radius:3px;
    font-family:Microsoft YaHei UI;
    selection-background-color:rgb(151, 198, 235);
    selection-color:rgb(0, 0, 0);""")

    def change_linenumber_color(self):
        global LINENUMBERCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(LINENUMBERCOLOR), msg_widget, "python记事本 - 颜色")
        LINENUMBERCOLOR = color.name()
        self.linenumber_color.setStyleSheet(f"color: {LINENUMBERCOLOR};")
        self._linenumber_color.setText(f"行号颜色: {LINENUMBERCOLOR.upper()}")

    def change_foreground_linenumber_color(self):
        global LINENUMBERFOREGROUNDCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(LINENUMBERFOREGROUNDCOLOR), msg_widget, "python记事本 - 颜色")
        LINENUMBERFOREGROUNDCOLOR = color.name()
        self._foreground_linenumber_color.setStyleSheet(f"color: {LINENUMBERFOREGROUNDCOLOR};")
        self._foreground_linenumber_color.setText(f"行号前景色: {LINENUMBERFOREGROUNDCOLOR.upper()}")

    def change_text_color(self):
        global TEXTCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(TEXTCOLOR), msg_widget, "python记事本 - 颜色")
        TEXTCOLOR = color.name()
        self.text_color.setStyleSheet(f"color: {TEXTCOLOR};")
        self._text_color.setText(f"文本框颜色: {TEXTCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_foreground_text_color(self):
        global TEXTFOREGROUNDCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(TEXTFOREGROUNDCOLOR), msg_widget, "python记事本 - 颜色")
        TEXTFOREGROUNDCOLOR = color.name()
        self.foreground_text_color.setStyleSheet(f"color: {TEXTFOREGROUNDCOLOR};")
        self._foreground_text_color.setText(f"文本框前景色: {TEXTFOREGROUNDCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_line_color(self):
        global LINECOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(LINECOLOR), msg_widget, "python记事本 - 颜色")
        LINECOLOR = color.name()
        self.line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._line_color.setText(f"行高亮颜色: {LINECOLOR.upper()}")

    def change_foreground_line_color(self):
        global FOREGROUNDLINECOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(FOREGROUNDLINECOLOR), msg_widget, "python记事本 - 颜色")
        FOREGROUNDLINECOLOR = color.name()
        self.foreground_line_color.setStyleSheet(f"color: {FOREGROUNDLINECOLOR};")
        self._foreground_line_color.setText(f"行高亮前景色: {FOREGROUNDLINECOLOR.upper()}")

    def change_selection_line_color(self):
        global SELECTIONCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(SELECTIONCOLOR), msg_widget, "python记事本 - 颜色")
        SELECTIONCOLOR = color.name()
        self.selection_line_color.setStyleSheet(f"color: {SELECTIONCOLOR};")
        self._selection_line_color.setText(f"被选择颜色: {SELECTIONCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_foreground_selection_line_color(self):
        global SELECTIONFOREGROUNDCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        msg_widget.setFont(FONT_)
        color: QColor = QColorDialog.getColor(QColor(SELECTIONFOREGROUNDCOLOR), msg_widget, "python记事本 - 颜色")
        SELECTIONFOREGROUNDCOLOR = color.name()
        self.foreground_selection_line_color.setStyleSheet(f"color: {SELECTIONFOREGROUNDCOLOR};")
        self._foreground_selection_line_color.setText(f"被选择前景色: {SELECTIONFOREGROUNDCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_font(self):
        global FONT, FONT_SIZE, FONT_FAMILY
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        msg_widget.setStyleSheet(WIDGET_STYLE_SHEET)
        font = QFontDialog.getFont(msg_widget)
        if font[1]:
            FONT = font[0]
            FONT_SIZE = FONT.pointSize()
            FONT_FAMILY = FONT.family()
            # self.ft.setFont(FONT_)
            self.ft.setText(
                f'字体: {FONT.family()}   大小: {FONT.pointSize()}   重量: {"较重" if FONT.bold() else "正常"} '
                f'下划线: {"有" if FONT.underline() else "无"} 删除线: {"有" if FONT.overline() else "无"}')
            for i in self.parents.text:
                i.setFont(FONT)
                i.text.setFont(FONT)
        self.parents.zoomed.setText(f"  {int(FONT.pointSize() * 100 / 12)}%  ")
        with open('.\\style\\font.tmp', 'wt') as fo:
            fo.write(f'font_family: {FONT_FAMILY}\nfont_size: {FONT_SIZE}')

    def exit(self):
        if not self.test:
            self.parents.setWindowTitle(
                f"python记事本 - {os.path.basename(self.parents.paths[self.parents.note.currentIndex()])}")
            self.un_draw()
        else:
            self.un_draw()
            sys.exit()
        # self.hide()


class SetWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1330, 700)
        self.setStyleSheet("background-color:white;")
        self.text = self.paths = []
        self.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Setting(SetWindow(), test=True)
    sys.exit(app.exec_())
