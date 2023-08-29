from PyQt5.QtGui import QFont
import getpass
USERNAME = getpass.getuser()
FONT = QFont()
FONT.setFamily("Microsoft YaHei UI")
FONT.setPointSize(12)
FONT_ = QFont()
FONT_.setFamily("Microsoft YaHei UI")
FONT_.setPointSize(12)
LINECOLOR = "#E5E5FF"
FOREGROUNDLINECOLOR = "#000000"
SELECTIONCOLOR = "#97C6EB"
SELECTIONFOREGROUNDCOLOR = "#000000"
LINENUMBERCOLOR = "#FFFFFF"
LINENUMBERFOREGROUNDCOLOR = "#4682B4"
TEXTCOLOR = "#FFFFFF"
TEXTFOREGROUNDCOLOR = "#000000"
STYLE_SHEET = ('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.03, y2:1, '
               '''stop:0 rgba(253, 253, 253, 255), stop:1 rgba(255, 255, 255, 255));
                  border:1px solid rgba(0, 0, 0, 0.1); border-radius:3px;border:1px solid rgb(50, 93, 136);
                  color:rgb(50, 93, 136);''')
with open("style-widget.qss")as fo:
    WIDGET_STYLE_SHEET = fo.read()
LAST_FONT_SIZE = 7
WRAP = True
