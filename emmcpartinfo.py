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

from multiprocessing import Process
from threading import Thread, Event

import pickle

import sys
import os
import emmcfunc
import emmctest


def getpartinfo(clsvar, msg_client) :

    emmcsl4a.disableAirplaneMode(False)




    ## ______________ gather the device info, and make the marker on device   __________________
    emmcfunc.gatherEmmcDeviceInfo(clsvar )

    ## ______________ setup of test parameters   __________________
    clsvar.setupMarkforUserdata = "crc32"  # "addrfillpartial", "addrfillfull"
    if clsvar.EmmcGBSize <= 8 :
        clsvar.sizetestblock = 16384  ## 8MB
    elif clsvar.EmmcGBSize <= 16 :
        clsvar.sizetestblock = 16384 * 2   ## 16MB
    else :
        clsvar.sizetestblock = 16384 * 4   ## 32MB

    listskipblockname = [ "persist", "mpt", "system", "cache"]
    clsvar.addrcrcstartblock = 0
    clsvar.crc0filladdress = False

    result = emmcfunc.skipCheckingBlock(clsvar, msg_client, listskipblockname)
    if result == False :
        msg_client.SendMsg("failed of skipCheckingBlock")
        exit()

    ## ______________ prepare the Partition with Mark .   __________________
    msg_client.SendMsg ("main before BuildCRC32Table" )

    result = emmcfunc.BuildCRC32Table(clsvar, msg_client)
    if result == False :
        msg_client.SendMsg("failed of BuildCRC32Table")
        exit()



    ## ______________ print the partition summary .   __________________
    emmcfunc.printpartitioninfo(clsvar, msg_client)



if __name__ == "__main__":
    ## ______________ initialize the variables class   __________________

    clsvar = emmcfunc.clsVariables()

    clsvar.pathmmc = emmcfunc.getEmmcPath(clsvar)
    clsvar.EmmcGBSize = emmcfunc.getEmmcGBSize(clsvar)
    clsvar.modelname = emmcfunc.getModelName(clsvar)
    clsvar.DeviceSerialNo = emmcfunc.getDeviceSerialNo(clsvar)
    clsvar.EmmcFirmwareVersion = emmcfunc.getEmmcFirmwareVersion(clsvar)
    clsvar.addrSPMIEMMCVDD = emmcfunc.getAddrSPMIEMMCVDD(clsvar)

    os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")

    # clsvar.modelname = "testmodel"
    # clsvar.DeviceSerialNo = "testNo"

    ## ______________ initialize the msg client class   __________________
    # SERVERIP = '172.21.26.41'
    SERVERIP = '192.168.219.152'


    msg_client = emmctest.clsMsgClent( clsvar.DeviceSerialNo,clsvar.modelname,SERVERIP )
    # msg_client.onlylocal = True

    msg_client.SendMsg("EmmcFirmwareVersion,%s"% clsvar.EmmcFirmwareVersion )
    msg_client.SendMsg ("curr dir : %s" % os.path.realpath("."))
    msg_client.SendMsg ("starting msg_client")



    clsvar.intervalrebuild = 8
    clsvar.currcountrebuild = 0



    ## ______________ launch the wake-up process   __________________
    runnerKey = Process( target=emmctest.taskGenKeyEvent, args=(clsvar,msg_client,))
    runnerKey.start()


    main_sec_start = int(round(time.time()))
    emmcfunc.setFakeEmmcWrite(clsvar, msg_client, True)

    try:

        getpartinfo(clsvar, msg_client)

    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("____Error : main ____")
        msg_client.SendMsg(msgerr)
        msg_client.SendMsg("finishing  main function" )



    sec_diff = int(round(time.time())) - main_sec_start
    msg_client.SendMsg("__ main loop collapsed time,%s"%(timedelta(seconds = sec_diff)))
    emmcfunc.setFakeEmmcWrite(clsvar, msg_client, False)

    runnerKey.terminate()

