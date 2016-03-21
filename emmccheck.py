# -*- coding: utf-8 -*-
from __future__ import print_function
# from importlib import reload
from datetime import timedelta
import time
import emmcsl4a
from emmcconfig import getModelInfo

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


def pretask(clsvar, msg_client) :

    emmcsl4a.disableAirplaneMode(False)

    msg_client.SendMsg ("main before tasksleep" )


    ## ______________ gather the device info, and make the marker on device   __________________
    emmcfunc.gatherEmmcDeviceInfo(clsvar )

    listskipblockname = [ "persist", "mpt", "system", "cache", "userdata"]
    clsvar.crc0filladdress = True
    clsvar.addrcrcstartblock = clsvar.userdata[0]


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

    ## ______________ save the clsvar .   __________________
    # with open('clsvar.pickle', 'wb') as handle:
    #     pickle.dump(clsvar, handle)
    #     msg_client.SendMsg("saved the clsvar.pickle")



    ## ______________ verify the Partition with the previous mark .   __________________
    # emmcfunc.setFakeEmmcWrite(clsvar, msg_client, True)


    ## ______________ print the partition summary .   __________________
    # emmcfunc.printpartitioninfo(clsvar, msg_client)


def posttask(clsvar, msg_client) :

    ## just after taskop =0 , we save the clsvar to storage.
    # emmcfunc.restoreUserdataWithZero(clsvar, msg_client)

    # emmcfunc.setFakeEmmcWrite(clsvar, msg_client, False)


    # with open('clsvar.pickle', 'wb') as handle:
    #     pickle.dump(clsvar, handle)

    msg_client.SendMsg("Main process is terminated...")


def main():
    os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")

    ## ______________ initialize the variables class   __________________
    # if os.path.exists("clsvar.pickle") :
    #     with open('clsvar.pickle', 'rb') as handle:
    #         clsvar = pickle.load(handle)
    # else :
    #     clsvar = emmcfunc.clsVariables()

    clsvar = emmcfunc.clsVariables()
    getModelInfo(clsvar)

    os.system("setenforce 0")

    ## ______________ setup of test parameters   __________________
    clsvar.pathmmc = emmcfunc.getEmmcPath(clsvar)
    clsvar.EmmcGBSize = emmcfunc.getEmmcGBSize(clsvar)
    clsvar.modelname = emmcfunc.getModelName(clsvar)
    clsvar.DeviceSerialNo = emmcfunc.getDeviceSerialNo(clsvar)
    clsvar.EmmcFirmwareVersion = emmcfunc.getEmmcFirmwareVersion(clsvar)
    clsvar.addrSPMIEMMCVDD = emmcfunc.getAddrSPMIEMMCVDD(clsvar)
    clsvar.sizetestblock = 8192

    # clsvar.modelname = "testmodel"
    # clsvar.DeviceSerialNo = "testNo"


    clsvar.taskname = "emmccheck"

    msg_client = emmctest.clsMsgClent( "%s_%s_%s"%(clsvar.taskname ,clsvar.DeviceSerialNo, clsvar.EmmcGBSize) ,clsvar.modelname,clsvar.SERVERIP, clsvar.port )
    msg_client.onlylocal = True
    msg_client.SendMsg("starting msg_client")

    #___________________________________________________________________________________
    # just for test
    # emmctest.printprocessmeminfo(clsvar, msg_client)
    # time.sleep(20)
    # exit()

    #___________________________________________________________________________________

    msg_client.SendMsg("clsvar.pathmmc,%s"%(clsvar.pathmmc))
    msg_client.SendMsg("clsvar.EmmcGBSize,%s"%(clsvar.EmmcGBSize))
    msg_client.SendMsg("clsvar.modelname,%s"%(clsvar.modelname))

    msg_client.SendMsg("clsvar.DeviceSerialNo,%s"%(clsvar.DeviceSerialNo))
    msg_client.SendMsg("clsvar.EmmcFirmwareVersion,%s"%(clsvar.EmmcFirmwareVersion))
    msg_client.SendMsg("clsvar.addrSPMIEMMCVDD,%s"%(clsvar.addrSPMIEMMCVDD))
    # msg_client.SendMsg("disableChargingEvent,%s"%(emmcfunc.disableChargingEvent(clsvar, True)))

    msg_client.SendMsg("getenforce,%s"% os.popen("getenforce 0").readline().strip() )


    emmcfunc.gatherEmmcDeviceInfo(clsvar )

    #____________________________________________________________________________________________
    # define the stressblock address if addrstressblock or namestressblock exist .
    addrstressblock = 0
    if hasattr(clsvar, "addrstressblock") and clsvar.addrstressblock != 0 :
        addrstressblock = clsvar.addrstressblock
    elif hasattr(clsvar, "namestressblock") and len(clsvar.namestressblock) != 0 :
        addrblock, size = emmcfunc.getpartitioninfo(clsvar, clsvar.namestressblock)
        addrstressblock = addrblock + ( size - clsvar.sizetestblock )
        # make addressblock to be module of clsvar.sizetestblock
        addrstressblock -= ( addrstressblock % clsvar.sizetestblock )
        if addrstressblock < addrblock :
            addrstressblock = 0


    if addrstressblock != 0 :
        if emmcfunc.fillblockwithblockaddresszero(clsvar, addrstressblock , clsvar.sizetestblock) == False :
            msg_client.SendMsg ("can't use the addrstressblock,%s" % addrstressblock )
            return
        else:
            clsvar.addrstressblock = addrstressblock
            msg_client.SendMsg ("addrstressblock,%s" % addrstressblock )

    #____________________________________________________________________________________________

    # clsvar.deepsleepsec = 30
    clsvar.currPreSleepSec = 1

    if not hasattr(clsvar, "deepsleepsec") or clsvar.deepsleepsec == None :
        clsvar.deepsleepsec = 20

    msg_client.SendMsg("deepsleepsec,%s"%clsvar.deepsleepsec)

    clsdeepsleep = emmcfunc.DeepSleepWake()
    countdeepsleepprev = emmcfunc.getDeepSleepCount(clsvar)
    msg_client.SendMsg("countdeepsleepprev is %s"%( countdeepsleepprev))

    clsvar.currEmmcWriteSize = 10

    for  aa in range(20) :

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countloop", "%s" % clsvar.currEmmcWriteSize)
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "retcheck", "%s" % 1)
        # assign  clsvar.addrstressblock to addrblockstart
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", clsvar.addrstressblock )
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", emmcfunc.CMD_FILLBLOCKRANDOMADDRESSZERO )

        # emmcfunc.disableChargingEvent(clsvar, False)
        # emmcfunc.disableChargingEvent(clsvar, True)

        time.sleep(clsvar.currPreSleepSec)

        clsdeepsleep.sleep(clsvar.deepsleepsec)

        try:
            time.sleep(clsvar.deepsleepsec+5)
            countdeepsleep = emmcfunc.getDeepSleepCount(clsvar)
            if ( countdeepsleepprev == countdeepsleep) :
                msg_client.SendMsg("No_Deep_Sleep")
            else:
                msg_client.SendMsg("countdeepsleep,%s"%countdeepsleep)
            countdeepsleepprev = countdeepsleep

        except:
            msg_client.SendMsg("fail,DeepSleepCountReadingError")

        result = emmcfunc.getEmmcDebugfsAttrValue(clsvar, "result")
        if  result != "0" :
            msg_client.SendMsg("fail,EmmcWriteError,%s"%result)



if __name__ == "__main__":
    main()