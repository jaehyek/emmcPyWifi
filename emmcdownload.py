# -*- coding: utf-8 -*-
from __future__ import print_function
import emmctest
import os

__author__ = 'jaehyek.choi'

from emmcconfig import getModelInfo

class CLSVAR():
    def __init__(self):
        pass

if __name__ == "__main__":
    os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")

    clsvar = CLSVAR()
    getModelInfo(clsvar)


    listls = emmctest.getfilesfromserver(clsvar.id, clsvar.passwd, clsvar.SERVERIP)

    print("downloaded files: \n")
    print(listls)



