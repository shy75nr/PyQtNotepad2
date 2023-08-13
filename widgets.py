import os.path
import time
from constants import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *




class CursorChangeButton(QPushButton):
    def enterEvent(self, a0: QMoveEvent) -> None:
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(a0)


class LineNumPaint(QWidget):
    def __init__(self, q_edit, parents=None):
        super().__init__(parents)
        self.q_edit_line_num = q_edit

    def sizeHint(self):
        return QSize(self.q_edit.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.q_edit_line_num.lineNumberAreaPaintEvent(event)


class PlainTextEditWithLineNum(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setLineWrapMode(QPlainTextEdit.NoWrap)  # 不自动换行
        self.lineNumberArea = LineNumPaint(self, parent)
        self.document().blockCountChanged.connect(self.update_line_num_width)
        self.document().cursorPositionChanged.connect(self.highlightCurrentLine)  # 高亮当前行
        self.verticalScrollBar().sliderMoved.connect(self.scroll_event)  # 滚动条移动更新行号
        self.update_line_num_width()

    def wheelEvent(self, d: QWheelEvent) -> None:
        self.scroll_event(d)
        super().wheelEvent(d)

    def scroll_event(self, event: QWheelEvent = None):
        self.lineNumberArea.update()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.lineNumberArea.update()
        self.highlightCurrentLine()

    def mousePressEvent(self, e: 'QMouseEvent') -> None:
        super().mousePressEvent(e)
        self.update()
        self.highlightCurrentLine()
        self.lineNumberArea.update()

    def mouseReleaseEvent(self, e: 'QMouseEvent') -> None:
        super().mouseReleaseEvent(e)
        self.update()
        self.highlightCurrentLine()
        self.lineNumberArea.update()

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
        painter.setFont(FONT)

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
        while block.isValid() and (top <= event.rect().bottom()) and blockNumber <= last_block_number:
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
        self.setFrameShape(QFrame.NoFrame)
        self.append = self.text.appendPlainText
        self.setText = self.text.setPlainText
        self.toText = self.text.toPlainText
        self.textCursor = self.text.textCursor
        self.clear = self.text.clear
        # stp = QScrollBar(self)
        # stp.resize(20, self.text.height() - 25)
        # stp.move(self.text.width() - 25, 0)
        # self.text.setHorizontalScrollBar(stp)

    def resize(self, *__args):
        super().resize(*__args)
        self.text.resize(*__args)


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


class Window(QScrollArea):
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
            self.opacity.i += 1
            if self.opacity.i >= 100:  # 此时透明度为1，即不透明，控件已经完全显示出来了
                self.timer.stop()  # 计时器停止
                self.timer.deleteLater()

        self.timer = QTimer()  # 计时器
        self.timer.setInterval(7)  # 设置间隔时间，毫秒为单位
        self.timer.timeout.connect(timeout)  # 超时槽函数，每到达间隔时间，调用该函数
        self.timer.start()  # 计时器开始

    def un_draw(self):
        self.opacity.i = 100  # 用于记录透明度变化与循环次数

        def timeout():  # 超时函数：改变透明度
            self.opacity.setOpacity(self.opacity.i / 100)
            self.setGraphicsEffect(self.opacity)  # 改变标签透明度
            self.opacity.i -= 1
            if self.opacity.i <= 0:  # 此时透明度为1，即不透明，控件已经完全显示出来了
                self.timer.stop()  # 计时器停止
                self.hide()
                self.timer.deleteLater()

        self.timer = QTimer()  # 计时器
        self.timer.setInterval(7)  # 设置间隔时间，毫秒为单位
        self.timer.timeout.connect(timeout)  # 超时槽函数，每到达间隔时间，调用该函数
        self.timer.start()  # 计时器开始


class Setting(Window):
    def __init__(self, parents: QMainWindow):
        super().__init__(parents)
        parents.setWindowTitle("python记事本 - 设置")
        self.parents = parents
        self.setFrameShape(QFrame.NoFrame)
        self.resize(parents.width(), parents.height())
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
        lb.move(100, 5)
        self.ft = QLabel(
            f'字体: {FONT.family()}   大小: {FONT.pointSize()}   重量: {"较重" if FONT.bold() else "正常"} '
            f'下划线: {"有" if FONT.underline() else "无"} 删除线: {"有" if FONT.overline() else "无"}', self)
        self.ft.setFont(FONT)
        self.ft.move(100, 100)
        self.ft.resize(1000, 30)
        change_font = CursorChangeButton("更改字体", self)
        change_font.setFont(FONT)
        change_font.move(950, 100)
        change_font.clicked.connect(self.change_font)
        change_font.setStyleSheet(STYLE_SHEET)
        self._line_color = QLabel(f"行高亮颜色: {LINECOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._line_color.move(100, 140)
        self._line_color.setFont(FONT)
        self._line_color.resize(280, 30)
        self.line_color = QLabel("████████████████████████████", self)
        self.line_color.move(380, 140)
        self.line_color.setStyleSheet(f"color: {LINECOLOR};")
        self.line_color.setFont(FONT)
        change_line_color = CursorChangeButton("更改颜色", self)
        change_line_color.setFont(FONT)
        change_line_color.move(950, 140)
        change_line_color.clicked.connect(self.change_line_color)
        change_line_color.setStyleSheet(STYLE_SHEET)
        self._foreground_line_color = QLabel(f"行高亮前景色: {FOREGROUNDLINECOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_line_color.move(100, 180)
        self._foreground_line_color.setFont(FONT)
        self._foreground_line_color.resize(280, 30)
        self.foreground_line_color = QLabel("████████████████████████████", self)
        self.foreground_line_color.move(380, 180)
        self.foreground_line_color.setStyleSheet(f"color: {FOREGROUNDLINECOLOR};")
        self.foreground_line_color.setFont(FONT)
        change_foreground_line_color = CursorChangeButton("更改颜色", self)
        change_foreground_line_color.setFont(FONT)
        change_foreground_line_color.move(950, 180)
        change_foreground_line_color.clicked.connect(self.change_foreground_line_color)
        change_foreground_line_color.setStyleSheet(STYLE_SHEET)
        self._foreground_selection_line_color = QLabel(f"被选择前景色: {SELECTIONFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_selection_line_color.move(100, 260)
        self._foreground_selection_line_color.setFont(FONT)
        self._foreground_selection_line_color.resize(280, 30)
        self.foreground_selection_line_color = QLabel("████████████████████████████", self)
        self.foreground_selection_line_color.move(380, 260)
        self.foreground_selection_line_color.setStyleSheet(f"color: {SELECTIONFOREGROUNDCOLOR};")
        self.foreground_selection_line_color.setFont(FONT)
        change_foreground_selection_line_color = CursorChangeButton("更改颜色", self)
        change_foreground_selection_line_color.setFont(FONT)
        change_foreground_selection_line_color.move(950, 260)
        change_foreground_selection_line_color.clicked.connect(self.change_foreground_selection_line_color)
        change_foreground_selection_line_color.setStyleSheet(STYLE_SHEET)
        self._selection_line_color = QLabel(f"被选择颜色: {SELECTIONCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._selection_line_color.move(100, 220)
        self._selection_line_color.setFont(FONT)
        self._selection_line_color.resize(240, 30)
        self.selection_line_color = QLabel("████████████████████████████", self)
        self.selection_line_color.move(380, 220)
        self.selection_line_color.setStyleSheet(f"color: {SELECTIONCOLOR};")
        self.selection_line_color.setFont(FONT)
        change_selection_line_color = CursorChangeButton("更改颜色", self)
        change_selection_line_color.setFont(FONT)
        change_selection_line_color.move(950, 220)
        change_selection_line_color.clicked.connect(self.change_selection_line_color)
        change_selection_line_color.setStyleSheet(STYLE_SHEET)
        self._linenumber_color = QLabel(f"行号颜色: {LINENUMBERCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._linenumber_color.move(100, 300)
        self._linenumber_color.setFont(FONT)
        self._linenumber_color.resize(280, 30)
        self.linenumber_color = QLabel("████████████████████████████", self)
        self.linenumber_color.move(380, 300)
        self.linenumber_color.setStyleSheet(f"color: {LINENUMBERCOLOR};")
        self.linenumber_color.setFont(FONT)
        change_linenumber_color = CursorChangeButton("更改颜色", self)
        change_linenumber_color.setFont(FONT)
        change_linenumber_color.move(950, 300)
        change_linenumber_color.clicked.connect(self.change_linenumber_color)
        change_linenumber_color.setStyleSheet(STYLE_SHEET)
        self._foreground_linenumber_color = QLabel(f"行号前景色: {LINENUMBERFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_linenumber_color.move(100, 340)
        self._foreground_linenumber_color.setFont(FONT)
        self._foreground_linenumber_color.resize(280, 30)
        self.foreground_linenumber_color = QLabel("████████████████████████████", self)
        self.foreground_linenumber_color.move(380, 340)
        self.foreground_linenumber_color.setStyleSheet(f"color: {LINENUMBERFOREGROUNDCOLOR};")
        self.foreground_linenumber_color.setFont(FONT)
        change_foreground_linenumber_color = CursorChangeButton("更改颜色", self)
        change_foreground_linenumber_color.setFont(FONT)
        change_foreground_linenumber_color.move(950, 340)
        change_foreground_linenumber_color.clicked.connect(self.change_foreground_linenumber_color)
        change_foreground_linenumber_color.setStyleSheet(STYLE_SHEET)
        self._text_color = QLabel(f"文本框颜色: {TEXTCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._text_color.move(100, 380)
        self._text_color.setFont(FONT)
        self._text_color.resize(280, 30)
        self.text_color = QLabel("████████████████████████████", self)
        self.text_color.move(380, 380)
        self.text_color.setStyleSheet(f"color: {TEXTCOLOR};")
        self.text_color.setFont(FONT)
        change_text_color = CursorChangeButton("更改颜色", self)
        change_text_color.setFont(FONT)
        change_text_color.move(950, 380)
        change_text_color.clicked.connect(self.change_text_color)
        change_text_color.setStyleSheet(STYLE_SHEET)
        self._foreground_text_color = QLabel(f"文本框前景色: {TEXTFOREGROUNDCOLOR.upper()}", self)
        # line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._foreground_text_color.move(100, 420)
        self._foreground_text_color.setFont(FONT)
        self._foreground_text_color.resize(280, 30)
        self.foreground_text_color = QLabel("████████████████████████████", self)
        self.foreground_text_color.move(380, 420)
        self.foreground_text_color.setStyleSheet(f"color: {TEXTFOREGROUNDCOLOR};")
        self.foreground_text_color.setFont(FONT)
        change_foreground_text_color = CursorChangeButton("更改颜色", self)
        change_foreground_text_color.setFont(FONT)
        change_foreground_text_color.move(950, 420)
        change_foreground_text_color.clicked.connect(self.change_foreground_text_color)
        change_foreground_text_color.setStyleSheet(STYLE_SHEET)
        self.show()

    def change_linenumber_color(self):
        global LINENUMBERCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(LINENUMBERCOLOR), msg_widget, "python记事本 - 颜色")
        LINENUMBERCOLOR = color.name()
        self.linenumber_color.setStyleSheet(f"color: {LINENUMBERCOLOR};")
        self._linenumber_color.setText(f"行号颜色: {LINENUMBERCOLOR.upper()}")

    def change_foreground_linenumber_color(self):
        global LINENUMBERFOREGROUNDCOLOR
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(LINENUMBERFOREGROUNDCOLOR), MSG_WIDGET, "python记事本 - 颜色")
        LINENUMBERFOREGROUNDCOLOR = color.name()
        self._foreground_linenumber_color.setStyleSheet(f"color: {LINENUMBERFOREGROUNDCOLOR};")
        self._foreground_linenumber_color.setText(f"行号景色: {LINENUMBERFOREGROUNDCOLOR.upper()}")

    def change_text_color(self):
        global TEXTCOLOR
        msg_widget = QWidget()
        msg_widget.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
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
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(TEXTFOREGROUNDCOLOR), MSG_WIDGET, "python记事本 - 颜色")
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
        color: QColor = QColorDialog.getColor(QColor(LINECOLOR), msg_widget, "python记事本 - 颜色")
        LINECOLOR = color.name()
        self.line_color.setStyleSheet(f"color: {LINECOLOR};")
        self._line_color.setText(f"行高亮颜色: {LINECOLOR.upper()}")

    def change_foreground_line_color(self):
        global FOREGROUNDLINECOLOR
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(FOREGROUNDLINECOLOR), MSG_WIDGET, "python记事本 - 颜色")
        FOREGROUNDLINECOLOR = color.name()
        self.foreground_line_color.setStyleSheet(f"color: {FOREGROUNDLINECOLOR};")
        self._foreground_line_color.setText(f"行高亮前景色: {FOREGROUNDLINECOLOR.upper()}")

    def change_selection_line_color(self):
        global SELECTIONCOLOR
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(SELECTIONCOLOR), MSG_WIDGET, "python记事本 - 颜色")
        SELECTIONCOLOR = color.name()
        self.selection_line_color.setStyleSheet(f"color: {SELECTIONCOLOR};")
        self._selection_line_color.setText(f"被选择颜色: {SELECTIONCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_foreground_selection_line_color(self):
        global SELECTIONFOREGROUNDCOLOR
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        color: QColor = QColorDialog.getColor(QColor(SELECTIONFOREGROUNDCOLOR), MSG_WIDGET, "python记事本 - 颜色")
        SELECTIONFOREGROUNDCOLOR = color.name()
        self.foreground_selection_line_color.setStyleSheet(f"color: {SELECTIONFOREGROUNDCOLOR};")
        self._foreground_selection_line_color.setText(f"被选择前景色: {SELECTIONFOREGROUNDCOLOR.upper()}")
        for i in self.parents.text:
            i.setStyleSheet(
                f"selection-background-color: {SELECTIONCOLOR};selection-color: {SELECTIONFOREGROUNDCOLOR};"
                f"color: {TEXTFOREGROUNDCOLOR};background-color: {TEXTCOLOR}")

    def change_font(self):
        MSG_WIDGET = QWidget()
        MSG_WIDGET.setWindowIcon(QIcon(".\\icon\\notepad.ico"))
        font = QFontDialog.getFont(MSG_WIDGET)
        if font[1]:
            global FONT
            FONT = font[0]
            # self.ft.setFont(FONT)
            self.ft.setText(
                f'字体: {FONT.family()}   大小: {FONT.pointSize()}   重量: {"较重" if FONT.bold() else "正常"} '
                f'下划线: {"有" if FONT.underline() else "无"} 删除线: {"有" if FONT.overline() else "无"}')
            for i in self.parents.text:
                i.setFont(FONT)
                i.text.setFont(FONT)

    def exit(self):
        self.parents.setWindowTitle(
            f"python记事本 - {os.path.basename(self.parents.paths[self.parents.note.currentIndex()])}")
        self.un_draw()
        # self.hide()
