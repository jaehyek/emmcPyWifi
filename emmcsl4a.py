# -*- coding: utf-8 -*-
from __future__ import print_function

import emmcfunc
import sl4a

def disableAirplaneMode( enable ):
    app = sl4a.Android()
    return app.toggleAirplaneMode(enable)

def wakeLockAcquireDim():
    app = sl4a.Android()
    return app.wakeLockAcquireDim()

def wakeLockAcquireFull():
    app = sl4a.Android()
    return app.wakeLockAcquireFull()

def wakeLockRelease():
    app = sl4a.Android()
    return app.wakeLockRelease()