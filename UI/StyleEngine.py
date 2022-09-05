import copy
import json
import os

from PyQt5 import QtGui, QtWidgets


class StyleEngine:
    """
    Dark Colours from https://stackoverflow.com/a/56851493
    """
    def __init__(self, app_ref, paths):
        self.__app = app_ref
        self.__paths = paths
        self.styles = {}
        
        for theme in sorted(os.listdir(self.__paths.themes_loc)):
            self.load_style(theme)
        
    @property
    def light_style(self):
        return {
            "window"          : [240, 240, 240],
            "window text"     : [  0,   0,   0],
            "base"            : [255, 255, 255],
            "alt base"        : [233, 231, 227],
            "tooltip base"    : [255, 255, 220],
            "tooltip text"    : [  0,   0,   0],
            "text"            : [  0,   0,   0],
            "button"          : [240, 240, 240],
            "button text"     : [  0,   0,   0],
            "bright text"     : [255, 255, 255],
            "link"            : [  0,   0, 255],
            "link visited"    : [255,   0, 255],
            "highlight"       : [  0, 120, 215],
            "highlighted text": [240, 240, 240],
            "light"           : [255, 255, 255],
            "midlight"        : [227, 227, 227],
            "mid"             : [160, 160, 160],
            "dark"            : [160, 160, 160],
            "shadow"          : [105, 105, 105]  
        }

    @property
    def dark_style(self):
        return {
            "window"          : [ 53,  53,  53],
            "window text"     : [255, 255, 255],
            "base"            : [ 25,  25,  25],
            "alt base"        : [ 53,  53,  53],
            "tooltip base"    : [  0,   0,   0],
            "tooltip text"    : [255, 255, 255],
            "text"            : [255, 255, 255],
            "button"          : [ 53,  53,  53],
            "button text"     : [255, 255, 255],
            "bright text"     : [255,   0,   0],
            "link"            : [ 42, 130, 218],
            "link visited"    : [255,   0, 255],
            "highlight"       : [ 42, 130, 218],
            "highlighted text": [  0,   0,   0],
            "light"           : [255, 255, 255],
            "midlight"        : [227, 227, 227],
            "mid"             : [160, 160, 160],
            "dark"            : [160, 160, 160],
            "shadow"          : [105, 105, 105]  
        }
    
    def load_style(self, file):
        filepath = os.path.join(self.__paths.themes_loc, file)
        filename, ext = os.path.splitext(file)
        if os.path.isfile(filepath) and ext.lstrip(os.extsep) == "json":
            with open(filepath, 'r') as F:
                style_def = json.load(F)
            name = filename
            
            self.styles[name] = style_def
        
    def save_style(self, name):
        filepath = os.path.join(self.__paths.themes_loc, os.extsep.join((name, "json")))
        with open(filepath, 'w') as F:
            json.dump(self.styles[name], F)
            
    def generate_style_name(self, name):
        stem, tail = name.rsplit(" ", 1)
        if tail.isdigit():
            number = int(tail)
            number += 1
            return stem + " " + str(number)
        else:
            return name + " 2"
        
    def generate_new_style_name(self, name):
        if name in self.styles:
            name = self.generate_style_name(name)
        return name

    def new_style(self, name, from_name):
        self.styles[name] = copy.deepcopy(self.styles[from_name])
        return name
        
    def apply_style(self, colour_map):
        default = self.light_style
        
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window,          QtGui.QColor(*colour_map.get("window",           default["window"])))
        palette.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(*colour_map.get("window text",      default["window text"])))
        palette.setColor(QtGui.QPalette.Base,            QtGui.QColor(*colour_map.get("base",             default["base"])))
        palette.setColor(QtGui.QPalette.AlternateBase,   QtGui.QColor(*colour_map.get("alt base",         default["alt base"])))
        palette.setColor(QtGui.QPalette.ToolTipBase,     QtGui.QColor(*colour_map.get("tooltip base",     default["tooltip base"])))
        palette.setColor(QtGui.QPalette.ToolTipText,     QtGui.QColor(*colour_map.get("tooltip text",     default["tooltip text"])))
        palette.setColor(QtGui.QPalette.Text,            QtGui.QColor(*colour_map.get("text",             default["text"])))
        palette.setColor(QtGui.QPalette.Button,          QtGui.QColor(*colour_map.get("button",           default["button"])))
        palette.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(*colour_map.get("button text",      default["button text"])))
        palette.setColor(QtGui.QPalette.BrightText,      QtGui.QColor(*colour_map.get("bright text",      default["bright text"])))
        palette.setColor(QtGui.QPalette.Link,            QtGui.QColor(*colour_map.get("link",             default["link"])))
        palette.setColor(QtGui.QPalette.LinkVisited,     QtGui.QColor(*colour_map.get("link visited",     default["link visited"])))
        palette.setColor(QtGui.QPalette.Highlight,       QtGui.QColor(*colour_map.get("highlight",        default["highlight"])))
        palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(*colour_map.get("highlighted text", default["highlighted text"])))
        palette.setColor(QtGui.QPalette.Light,           QtGui.QColor(*colour_map.get("light",            default["light"])))
        palette.setColor(QtGui.QPalette.Midlight,        QtGui.QColor(*colour_map.get("midlight",         default["midlight"])))
        palette.setColor(QtGui.QPalette.Mid,             QtGui.QColor(*colour_map.get("mid",              default["mid"])))
        palette.setColor(QtGui.QPalette.Dark,            QtGui.QColor(*colour_map.get("dark",             default["dark"])))
        palette.setColor(QtGui.QPalette.Shadow,          QtGui.QColor(*colour_map.get("shadow",           default["shadow"])))
        
        self.__app.setPalette(palette)
        
    def get_active_style(self):
        return self.__extract_style()
        
    def __extract_style(self):
        palette = QtWidgets.QApplication.palette()
        
        style = {}
        style["window"]           = self.__extract_colour(palette.window())
        style["window text"]      = self.__extract_colour(palette.windowText())
        style["base"]             = self.__extract_colour(palette.base())
        style["alt base"]         = self.__extract_colour(palette.alternateBase())
        style["tooltip base"]     = self.__extract_colour(palette.toolTipBase())
        style["tooltip text"]     = self.__extract_colour(palette.toolTipText())
        style["text"]             = self.__extract_colour(palette.text())
        style["button"]           = self.__extract_colour(palette.button())
        style["button text"]      = self.__extract_colour(palette.buttonText())
        style["bright text"]      = self.__extract_colour(palette.brightText())
        style["link"]             = self.__extract_colour(palette.link())
        style["link visited"]     = self.__extract_colour(palette.linkVisited())
        style["highlight"]        = self.__extract_colour(palette.highlight())
        style["highlighted text"] = self.__extract_colour(palette.highlightedText())
        style["light"]            = self.__extract_colour(palette.light())
        style["midlight"]         = self.__extract_colour(palette.midlight())
        style["mid"]              = self.__extract_colour(palette.mid())
        style["dark"]             = self.__extract_colour(palette.dark())
        style["shadow"]           = self.__extract_colour(palette.shadow())
        
        return style
        
    def __extract_colour(self, brush):
        bcol = brush.color()
        return [bcol.red(), bcol.green(), bcol.blue()]