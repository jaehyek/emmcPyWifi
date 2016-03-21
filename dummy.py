# -*- coding: utf-8 -*-
from __future__ import print_function
import time

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""


import sys
import os
import emmcfunc
import emmctest
def funcnull():
    pass


def main():
    # initialize the variables
    clsvar = emmcfunc.clsVariables()

    # the below is for python 2
    if not hasattr(clsvar,"adb") :
        if sys.version[0] == "2" :
            sys.stdout.flush = funcnull
            sys.stderr.flush = funcnull

        os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")


    clsvar.pathmmc = "/sys/kernel/debug/mmc0/mmc0:0001"
    # clsvar.pathmmc = "/sys/kernel/debug/mmc1/mmc1:0001"
    clsvar.modelname = emmcfunc.getModelName(clsvar)
    clsvar.DeviceSerialNo = emmcfunc.getDeviceSerialNo(clsvar)
    clsvar.EmmcFirmwareVersion = emmcfunc.getEmmcFirmwareVersion(clsvar)
    #
    emmcfunc.gatherEmmcDeviceInfo(clsvar )


    print (clsvar.modelname)
    print (clsvar.serial)
    print (clsvar.EmmcFirmwareVersion)



    # clsvar.modelname = "testmodel"
    # clsvar.DeviceSerialNo = "testNo"

    SERVERIP = '172.21.26.41'
    id = 'ysc'
    passwd = 'lge123'

    # SERVERIP = '192.168.219.180'
    # id = 'jaehyek'
    # passwd = 'choi'

    msg_client = emmctest.clsMsgClent( clsvar.DeviceSerialNo,clsvar.modelname,SERVERIP )
    msg_client.onlylocal = True


    msg_client.SendMsg("EmmcFirmwareVersion,%s"% clsvar.EmmcFirmwareVersion )
    msg_client.SendMsg ("curr dir : %s" % os.path.realpath("."))
    msg_client.SendMsg ("starting msg_client")


    # emmctest.makeKeyEventPowerKey()
    # emmctest.displayoff()

    clsvar.allstop.Value = 0

    # emmctest.taskEmmcRandomWrite(clsvar, msg_client)


    if emmcfunc.setupRandomWriteAddr( clsvar, msg_client) == False :
        msg_client.SendMsg("failed to setupRandomWriteAddr")
        print ("failed to setupRandomWriteAddr")
        return False

    clsvar.countlifemeasure = str(100)
    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)

    start, size = emmcfunc.getpartitioninfo(clsvar, "userdata")
    start = int(start)
    size = int(size)
    start = start + int(size/2)
    size = int(size/2)

    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(start))
    msg_client.SendMsg("addrblockstart,%s"%start)

    loop = 100
    while(loop > 0 ) :
        clsvar.emmccountloop = "-1"
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countloop", "%s" % clsvar.emmccountloop)
        msg_client.SendMsg("Before Looping in funcLoopWritingWithSaving ")
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", "12" )
        msg_client.SendMsg("After Looping in funcLoopWritingWithSaving ")

        # print the attribute : countrepeated
        msg_client.SendMsg("eMMC countrepeated , %s " % emmcfunc.getEmmcDebugfsAttrValue(clsvar, "countrepeated"))

        loop -= 1
        time.sleep(2)
        print("emmc Write Job again")


if __name__ == "__main__":
    main()