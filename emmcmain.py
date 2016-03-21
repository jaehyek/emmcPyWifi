# -*- coding: utf-8 -*-
from __future__ import print_function
# from importlib import reload
from datetime import timedelta
import time
from emmcconfig import getModelInfo
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


def pretask(clsvar, msg_client) :
    if clsvar.boolbuildcrc32 == False :
        return

    emmcsl4a.disableAirplaneMode(False)

    msg_client.SendMsg ("main before tasksleep" )

    listskipblockname = [ "persist", "mpt", "system", "cache", "userdata"]

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
    emmcfunc.printpartitioninfo(clsvar, msg_client)


def posttask(clsvar, msg_client) :

    ## just after taskop =0 , we save the clsvar to storage.
    # emmcfunc.restoreUserdataWithZero(clsvar, msg_client)

    # emmcfunc.setFakeEmmcWrite(clsvar, msg_client, False)


    # with open('clsvar.pickle', 'wb') as handle:
    #     pickle.dump(clsvar, handle)

    msg_client.SendMsg("Main process is terminated...")


def main(taskname):

    if not taskname in [ "sleep", "ref", "keepread","keepwrite", "poweronoff", "printemmcblockinfo"] :
        print("Not functioned.")
        return

    os.chdir("/sdcard/com.hipipal.qpyplus/scripts3")

    clsvar = emmcfunc.clsVariables()
    os.system("setenforce 0")
    getModelInfo(clsvar)

    ## ______________ setup of test parameters   __________________
    clsvar.pathmmc = emmcfunc.getEmmcPath(clsvar)
    clsvar.EmmcGBSize = emmcfunc.getEmmcGBSize(clsvar)
    clsvar.modelname = emmcfunc.getModelName(clsvar)
    clsvar.DeviceSerialNo = emmcfunc.getDeviceSerialNo(clsvar)
    clsvar.EmmcFirmwareVersion = emmcfunc.getEmmcFirmwareVersion(clsvar)
    clsvar.addrSPMIEMMCVDD = emmcfunc.getAddrSPMIEMMCVDD(clsvar)

    clsvar.intervalrebuild = 10000
    clsvar.currcountrebuild = 0
    clsvar.sizetestblock = 8192
    clsvar.taskname = taskname

    msg_client = emmctest.clsMsgClent( "%s_%s_%s"%(clsvar.taskname ,clsvar.DeviceSerialNo, clsvar.EmmcGBSize) ,clsvar.modelname,clsvar.SERVERIP, clsvar.port )
    # msg_client.onlylocal = True

    clsvar.msg_client = msg_client
    msg_client.SendMsg ("starting msg_client")

    msg_client.SendMsg("EmmcFirmwareVersion,%s"% clsvar.EmmcFirmwareVersion )
    msg_client.SendMsg ("curr dir,%s" % os.path.realpath("."))

    msg_client.SendMsg ("modelname,%s" % clsvar.modelname)
    msg_client.SendMsg ("pathmmc,%s" % clsvar.pathmmc)
    msg_client.SendMsg ("EmmcGBSize,%s" % clsvar.EmmcGBSize)
    msg_client.SendMsg ("addrSPMIEMMCVDD,%s" % clsvar.addrSPMIEMMCVDD)
    msg_client.SendMsg ("taskname,%s" % clsvar.taskname)
    msg_client.SendMsg ("clsvar.sizetestblock,%s"%(clsvar.sizetestblock) )
    msg_client.SendMsg("getenforce,%s"% os.popen("getenforce 0").readline().strip() )


    ## ______________ launch the wake-up process   __________________
    # runnerKey = Process( target=emmctest.taskGenKeyEvent, args=(clsvar,msg_client,))
    # runnerKey.start()

    ## ______________ gather the device info, and make the marker on device   __________________
    emmcfunc.gatherEmmcDeviceInfo(clsvar )
    clsvar.crc0filladdress = True
    clsvar.addrcrcstartblock = clsvar.userdata[0]

    main_sec_start = int(round(time.time()))

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

    try:
        if taskname == "printemmcblockinfo" :
            runnertask = Process( target=emmcfunc.printEmmcBlockinfo, args=(clsvar, msg_client,))
            runnertask.start()

        elif taskname == "sleepwakeCRC32not" :
            runnertask = Process( target=emmctest.scenario_sleepwakeCRC32not, args=(clsvar, msg_client,))
            runnertask.start()
        elif hasattr(clsvar, "skipCRC32build") and clsvar.skipCRC32build == True :
            pass
        else:
            # pass
            pretask(clsvar, msg_client)
            # clsvar.addrstressblock = 12197888 + 16384000


        if clsvar.taskname == "sleep" :
            runnertask = Process( target=emmctest.scenario_sleepwake, args=(clsvar, msg_client,))
            runnertask.start()

        elif clsvar.taskname == "ref" :
            runnertask = Process( target=emmctest.scenario_referring, args=(clsvar, msg_client,))
            runnertask.start()

        elif clsvar.taskname == "keepread" :
            runnertask = Process( target=emmctest.scenario_keepread, args=(clsvar, msg_client,))
            runnertask.start()

        elif clsvar.taskname == "keepwrite" :
            runnertask = Process( target=emmctest.scenario_keepwrite, args=(clsvar, msg_client,))
            runnertask.start()

        elif clsvar.taskname == "poweronoff" :
            runnertask = Process( target=emmctest.scenario_poweronoff, args=(clsvar, msg_client,))
            runnertask.start()

        # else:
        #     runnertask = Process( target=emmctest.scenario_VDDShaking, args =(clsvar, msg_client,))
        #     runnertask.start()

        while(True):
            time.sleep(60)
            # if runnerKey.is_alive() == False :
            #     runnerKey.terminate()
            #     runnerKey = 0
            #     runnerKey = Process( target=emmctest.taskGenKeyEvent, args=(clsvar,msg_client,))
            #     runnerKey.start()

            if runnertask.is_alive() == False :
                break

        posttask(clsvar, msg_client)

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
    # emmcfunc.setFakeEmmcWrite(clsvar, msg_client, False)

    # runnerKey.terminate()
