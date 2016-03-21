# -*- coding: utf-8 -*-
from __future__ import print_function
__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""


import emmcfunc
import emmctest
import os


def prepareEmmcLDO20():
    os.system('adb shell "echo 0x15340  > /sys/kernel/debug/spmi/spmi-0/address"')
    os.system('adb shell "echo 2 > /sys/kernel/debug/spmi/spmi-0/count"')
    os.system('adb shell "echo 0x3 > /sys/kernel/debug/spmi/spmi-0/save0"')
    os.system('adb shell "echo 0x3a > /sys/kernel/debug/spmi/spmi-0/save1"')



def main(clsvar):

    clsvar.pathmmc = "/sys/kernel/debug/mmc0/mmc0:0001"
    clsvar.modelname = "model"
    clsvar.DeviceSerialNo = "serialNO"
    clsvar.EmmcFirmwareVersion = "Firmware"

    prepareEmmcLDO20()

    print ("currEmmcVDD:%s, %s" % (clsvar.currEmmcVDD,int(clsvar.currEmmcVDD) * 0.025 + 1.5) )
    print ("mtimeSleepup:%s" % clsvar.mtimeSleepup)
    print ("mtimeSleepdown:%s" % clsvar.mtimeSleepdown)
    print ("countloop:%s" % clsvar.currcountLDO20shaking)

    # totaltime = int(int(clsvar.currcountLDO20shaking) * int(clsvar.mtimeSleepup) * int(clsvar.mtimeSleepdown) / 1000)
    # print ( "totaltime:%s"%(totaltime))

    os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/countloop"' % clsvar.currcountLDO20shaking )
    os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/mtimeSleepup"' % clsvar.mtimeSleepup )
    os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/mtimeSleepdown"' % clsvar.mtimeSleepdown )
    os.system('adb shell "echo %s %s > /sys/kernel/debug/spmi/spmi-0/cmdloop"' % (3, clsvar.currEmmcVDD ))



if __name__ == "__main__":

    import argparse
    fileincsv = ""

    clsvar = emmcfunc.clsVariables()

    cmdlineopt = argparse.ArgumentParser( description='mspmi')
    cmdlineopt.add_argument("currEmmcVDD")
    cmdlineopt.add_argument("mtimeSleepup")
    cmdlineopt.add_argument("mtimeSleepdown")
    cmdlineopt.add_argument("currcountLDO20shaking")

    cmdlineresults = cmdlineopt.parse_args()


    clsvar.currEmmcVDD = cmdlineresults.currEmmcVDD
    clsvar.mtimeSleepup = cmdlineresults.mtimeSleepup
    clsvar.mtimeSleepdown = cmdlineresults.mtimeSleepdown
    clsvar.currcountLDO20shaking = cmdlineresults.currcountLDO20shaking

    main(clsvar)


    # try:
    #     main()
    # except Exception as e:
    #     import traceback
    #
    #
    #     strReportFileName = "ErrorReprot" + ".txt"
    #     f = open(strReportFileName, "w")
    #
    #     f.write("Error Message : \n")
    #     f.write(traceback.format_exc())
    #
    #     f.close()
