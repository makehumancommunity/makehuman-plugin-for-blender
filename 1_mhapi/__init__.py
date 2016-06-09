#!/usr/bin/python

__all__ = ["api","namespace"]

from api import API

def load(app):
    app.mhapi = API(app)

def unload(app):
    pass

