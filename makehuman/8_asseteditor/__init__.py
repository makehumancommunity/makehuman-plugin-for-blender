#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman community assets

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius, Aranuvir

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin edits assets

"""

import gui3d
import mh
import gui
import log

from asseteditor import AssetEditorTaskView

category = None

editorView = None

def load(app, category=None):
    category = app.getCategory('Community')
    editorView = category.addTask(AssetEditorTaskView(category))

def unload(app):
    pass