# -*- coding: utf-8 -*-
import os

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""

import emmcfunc

def main():
    pass



if __name__ == "__main__":


    os.system("adb shell cat /sys/kernel/debug/rpm_stats")
    print ("--------------------------------------------------------------------------")
    os.system("adb shell ls /sys/module/qpnp_linear_charger/parameters")
    print ("--------------------------------------------------------------------------")

    clsvar = emmcfunc.clsVariables()

    clsvar.EmmcFirmwareVersion = emmcfunc.getEmmcFirmwareVersion(clsvar)
    clsvar.EmmcGBSize = emmcfunc.getEmmcGBSize(clsvar)
    serialno = emmcfunc.getDeviceSerialNo(clsvar)[6:]
    lifevalue = emmcfunc.getEmmcLifeValueofext_csd(clsvar)
    clsvar.modelname = emmcfunc.getModelName(clsvar)
    manfid = emmcfunc.getManfID(clsvar)

    print ("modelname: %s" % clsvar.modelname)
    print ("firmwarever: %s" % clsvar.EmmcFirmwareVersion)
    print ("EmmcGBSize : %s" % clsvar.EmmcGBSize)
    print ("serialno   : %s" % serialno)
    print ("lifevalue  : %s" % lifevalue)
    print ("manfid  : %s" % manfid)
    print ("--------------------------------------------------------------------------")
    emmcfunc.gatherEmmcDeviceInfo(clsvar )
    print ("--------------------------------------------------------------------------")



    f = open("devicelist.txt", 'a')
    f.write("modelname,%s,firmwarever,%s,EmmcGBSize,%s,serialno,%s,lifevalue,%s,manfid,%s \n"%(clsvar.modelname,clsvar.EmmcFirmwareVersion,clsvar.EmmcGBSize,serialno,lifevalue,manfid))
    f.close()