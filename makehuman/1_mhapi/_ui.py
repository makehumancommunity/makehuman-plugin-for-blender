#!/usr/bin/python

from namespace import NameSpace

import gui3d
import mh
import gui
import log

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *

from progress import Progress

from core import G

class ComboBox(QtGui.QComboBox, QtGui.QWidget):

    onChangeMethod = None

    def __init__(self,data = None, onChange = None):
        super(ComboBox, self).__init__()
        self.currentIndexChanged.connect(self._onChange)
        if data:
            self.setData(data)
        if onChange:
            self.onChangeMethod = onChange

        # Padding is because Qt has a bug that ignores style color in a 
        # combobox without it (for some incomprehensible reason)
        self.setStyleSheet("QComboBox { color: white; padding: 2px }")

    def setData(self,items):
        self.clear()
        for item in items:
            self.addItem(item)

    def getCurrentItem(self):
        return self.currentText()

    def rowCount(self):
        return len( [item for item in self.getItems() if not item.isHidden()] )

    def setCurrentRow(self,row):
        self.setCurrentIndex(row)

    def setCurrentItem(self,itemText):
        index = self.findText(itemText, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)

    def setOnChange(self,onChange):
        self.onChangeMethod = onChange

    def _onChange(self):
        log.debug("onChange")
        if self.onChangeMethod:
            self.onChangeMethod(self.getCurrentItem())

class UI(NameSpace):
    """This namespace wraps all calls that are related to working with the user interface."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def createWidget(self):
        return gui.Widget()

    def createTab(self,parent,name,label):
        return gui.Tab(parent,name,label)

    def createGroupBox(self,label):
        return gui.GroupBox(label)

    def createSlider(self, value=0.0, min=0.0, max=1.0, label=None, vertical=False, valueConverter=None, image=None, scale=1000):
        return gui.Slider(value,min,max,label,vertical,valueConverter,image,scale)

    def createButton(self, label=None, selected=False):
        return gui.Button(label,selected)

    def createCheckBox(self, label=None, selected=False):        
        return gui.CheckBox(label,selected)

    def createComboBox(self, data = None, onChange = None):
        return ComboBox(data, onChange)

    def createList(self, data=None):
        l = gui.ListView()
        if data:
            l.setData(data)
        return l

    def createLabel(self, label=''):
        return gui.TextView(label)

    def createTextEdit(self, text='', validator = None):        
        return gui.TextEdit(text,validator)





