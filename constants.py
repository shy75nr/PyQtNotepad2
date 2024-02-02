import json
import re
from PyQt5.QtGui import *
import getpass

USERNAME = getpass.getuser()
FONT = QFont()
FONT_TEXT = re.compile(r'''font_family: (.+)
font_size: (\d+)''')
with open('.\\style\\font.tmp', 'rt') as fo:
    FONT_FAMILY, FONT_SIZE = FONT_TEXT.match(fo.read()).groups()
FONT.setFamily(FONT_FAMILY)
FONT.setPointSize(eval(FONT_SIZE))
FONT_ = QFont()
FONT_.setFamily("Microsoft YaHei UI")
FONT_.setPointSize(12)
ERROR_TEXT = ''
with (open('.\\style\\settings.json', 'rt') as fo,
      open('.\\style\\出厂设置.json') as error):
    try:
        x = json.load(fo)
    except json.JSONDecodeError:
        ERROR_TEXT += "\nsettings.json无法识别"
        try:
            x = json.load(error)
        except json.JSONDecodeError:
            x = {
                "linecolor": "#E5E5FF",
                "fglinecolor": "#000000",
                "selectioncolor": "#97C6EB",
                "selectionfgcolor": "#000000",
                "linenumcolor": "#FFFFFF",
                "linenumfgcolor": "#4682B4",
                "textcolor": "#FFFFFF",
                "textfgcolor": "#6E6D69",
                "web": "https://cn.bing.com/search?q=$KEYWORD$",
                "lastfontsize": 7,
                "wrap": True
            }
            ERROR_TEXT += "\n出厂设置.json无法识别"
        with open(".\\style\\settings.json", "wt") as f:
            f.write(json.dumps(x))
LINECOLOR = x['linecolor']
FOREGROUNDLINECOLOR = x['fglinecolor']
SELECTIONCOLOR = x['selectioncolor']
SELECTIONFOREGROUNDCOLOR = x['selectionfgcolor']
LINENUMBERCOLOR = x['linenumcolor']
LINENUMBERFOREGROUNDCOLOR = x['linenumfgcolor']
TEXTCOLOR = x['textcolor']
TEXTFOREGROUNDCOLOR = x['textfgcolor']
STYLE_SHEET = ('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.03, y2:1, '
               '''stop:0 rgba(253, 253, 253, 255), stop:1 rgba(255, 255, 255, 255));
                  border:1px solid rgba(0, 0, 0, 0.1); border-radius:3px;border:1px solid rgb(50, 93, 136);
                  color:rgb(50, 93, 136);''')
WEB = x['web']
with open(".\\style\\style-widget.qss") as fo:
    WIDGET_STYLE_SHEET = fo.read()
LAST_FONT_SIZE = x['lastfontsize']
WRAP = True

with open(".\\style\\about.txt", encoding="utf-8") as fo:
    ABOUT = fo.read()
OUTLINE = """border-radius:3px;
    border:2px solid rgb(50, 93, 136);
    font-family:Microsoft YaHei UI;
    background-color:rgb({});
    color:rgb({});"""
