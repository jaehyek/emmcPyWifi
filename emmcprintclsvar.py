# -*- coding: utf-8 -*-
from __future__ import print_function
# from importlib import reload
from datetime import timedelta
import time
import emmcsl4a

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""


import pickle

import sys
import os
import emmcfunc
import emmctest


if __name__ == "__main__":
    os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")

    ## ______________ initialize the variables class   __________________
    if os.path.exists("clsvar.pickle") :
        with open('clsvar.pickle', 'rb') as handle:
            clsvar = pickle.load(handle)
    else :
        print("No clsvar.pickle")
        exit()


    # clsvar.modelname = "testmodel"
    # clsvar.DeviceSerialNo = "testNo"

    ## ______________ initialize the msg client class   __________________
    # SERVERIP = '172.21.26.41'
    SERVERIP = '192.168.219.152'


    msg_client = emmctest.clsMsgClent( clsvar.DeviceSerialNo,clsvar.modelname,SERVERIP )
    # msg_client.onlylocal = True

    emmcfunc.printpartitioninfo(clsvar, msg_client)

