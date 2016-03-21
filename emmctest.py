# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import timedelta

import os
import sys
import emmcfunc

from socket import socket, AF_INET, SOCK_STREAM
from ftplib import FTP
import time
import inspect
import threading

from multiprocessing import Process

import emmcsl4a


def printprocessmeminfo(clsvar,msg_client) :
    listinfo = os.popen("procrank").readlines()
    for line in listinfo :
        if "hipipal" in line :
            listitems = line.split()
            msg_client.SendMsg("ProcRandk,Rss,%s,Pss,%s,Uss,%s,pname,%s"%(listitems[2], listitems[3], listitems[4],listitems[-1].strip() ))
        elif "RAM" in line  and "free" in line :
            listitems = line.split(",")
            msg_client.SendMsg("freeMem,%s"%(listitems[1]))



class AsynchronousRunner(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''
    def __init__(self, func,param1,param2):
        threading.Thread.__init__(self)
        self.func = func
        self.param1 = param1
        self.param2 = param2


    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        self.func(self.param1, self.param2)



def getfilesfromserver( id, passwd, ftpd = '172.21.26.41' ):
    try:
        ftp = FTP(ftpd)
        ftp.login(id, passwd)
        ftp.cwd('')
        ftp.cwd('proj')
        ftp.cwd('scripts')
        ftp.cwd('cmds')
        listls = ftp.nlst()
        print (listls)
        for filename in listls :
            ftp.retrbinary('RETR %s' % filename, open('%s' % filename, 'wb').write)
        ftp.quit()

        return listls
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
        return []

class clsMsgClent():
    def __init__(self,ID="id",modelname="model", address='172.21.26.41', port=20000):
        self.address = address
        self.ID = ID
        self.modelname = modelname
        self.port = port
        self.NoRetry = 5
        self.onlylocal = False
        self.s = 0
        # self.CreateSocket()

    def CreateSocket(self):
        temptry = self.NoRetry
        while temptry :
            try:
                self.s = socket(AF_INET, SOCK_STREAM)
                self.s.connect((self.address, self.port))
                break
            except :
                print ("can't connect to sever ")
                time.sleep(1)
                print ("retry to connect ")
                temptry -= 1
        if temptry == 0 :
            del self.s
            self.s = 0
            return False
        else:
            return True
    def SendMsg(self, msg):
        print(msg)
        if (self.onlylocal == True) :
            return

        if self.s == 0 :
            if self.CreateSocket() == False :
                print("Cant Create socket")
                return

        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        # caution:  \n  must be attached.
        # msg = self.ID + "," + self.modelname + "," + mod.__name__ + "," +  msg + "\n"
        msg = self.ID + "," + self.modelname + "," + calframe[1][3] + "," +  msg + "\n"
        temptry = self.NoRetry

        while(temptry):
            try:
                self.s.send(msg.encode())
                resp = self.s.recv(8192)
                break
            except :
                print ("trying to send msg ....")
                self.CreateSocket()
                temptry -= 1
                continue
        if temptry == 0 :
            self.s.close()
            print ('fail to send msg .....')



def disableChargerEvent(clsvar, enable) :
    if not enable in [ 0, 1 ]:
        print("invalid enable parameter")
        return
    filedisablechargeevent = "/sys/module/qpnp_charger/parameters/qpnp_sleep_enable"
    try:
        open(filedisablechargeevent, "w").write("%s"%enable)
    except:
        print ("unable to write value to file")

def displayoff():
    attrfile = "/sys/class/graphics/fb0/blank"
    open(attrfile, "w").write("4")

def displayon():
    attrfile = "/sys/class/graphics/fb0/blank"
    open(attrfile, "w").write("0")


def emmctest(clsvar, msg_client):
    print ("starting msg_client")
    time.sleep(1)
    emmcfunc.emmcfunc(clsvar, msg_client)
    msg_client.SendMsg("emmctest function 33333 " )

    # clsvar = emmcfunc.clsVariables()
    #
    # clsvar.__dict__["pathmmc"] = "/sys/kernel/debug/mmc0/mmc0:0001"
    # # clsvar.__dict__["pathmmc"] = "/sys/kernel/debug/mmc1/mmc1:0001"
    # clsvar.__dict__["modelname"] = emmcfunc.getModelName()
    # clsvar.__dict__["DeviceSerialNo"] = emmcfunc.getDeviceSerialNo()

    # emmcfunc.gatherEmmcDeviceInfo(clsvar )



    # print clsvar.modelname
    # print clsvar.serial



    # msg_client = clsMsgClent(clsvar.DeviceSerialNo,clsvar.modelname,'127.0.0.1' )
    # loop = 5
    # while loop  :
    #     msg_client.SendMsg("hello_%s" % loop )
    #     time.sleep(1)
    #     loop -= 1

'''
usage: input [text|keyevent]
  input text <string>
  input keyevent <event_code>

0 -->  "KEYCODE_UNKNOWN"
1 -->  "KEYCODE_MENU"
2 -->  "KEYCODE_SOFT_RIGHT"
3 -->  "KEYCODE_HOME"
4 -->  "KEYCODE_BACK"
5 -->  "KEYCODE_CALL"
6 -->  "KEYCODE_ENDCALL"
7 -->  "KEYCODE_0"
8 -->  "KEYCODE_1"
9 -->  "KEYCODE_2"
10 -->  "KEYCODE_3"
11 -->  "KEYCODE_4"
12 -->  "KEYCODE_5"
13 -->  "KEYCODE_6"
14 -->  "KEYCODE_7"
15 -->  "KEYCODE_8"
16 -->  "KEYCODE_9"
17 -->  "KEYCODE_STAR"
18 -->  "KEYCODE_POUND"
19 -->  "KEYCODE_DPAD_UP"
20 -->  "KEYCODE_DPAD_DOWN"
21 -->  "KEYCODE_DPAD_LEFT"
22 -->  "KEYCODE_DPAD_RIGHT"
23 -->  "KEYCODE_DPAD_CENTER"
24 -->  "KEYCODE_VOLUME_UP"
25 -->  "KEYCODE_VOLUME_DOWN"
26 -->  "KEYCODE_POWER"
27 -->  "KEYCODE_CAMERA"
28 -->  "KEYCODE_CLEAR"
29 -->  "KEYCODE_A"
30 -->  "KEYCODE_B"
31 -->  "KEYCODE_C"
32 -->  "KEYCODE_D"
33 -->  "KEYCODE_E"
34 -->  "KEYCODE_F"
35 -->  "KEYCODE_G"
36 -->  "KEYCODE_H"
37 -->  "KEYCODE_I"
38 -->  "KEYCODE_J"
39 -->  "KEYCODE_K"
40 -->  "KEYCODE_L"
41 -->  "KEYCODE_M"
42 -->  "KEYCODE_N"
43 -->  "KEYCODE_O"
44 -->  "KEYCODE_P"
45 -->  "KEYCODE_Q"
46 -->  "KEYCODE_R"
47 -->  "KEYCODE_S"
48 -->  "KEYCODE_T"
49 -->  "KEYCODE_U"
50 -->  "KEYCODE_V"
51 -->  "KEYCODE_W"
52 -->  "KEYCODE_X"
53 -->  "KEYCODE_Y"
54 -->  "KEYCODE_Z"
55 -->  "KEYCODE_COMMA"
56 -->  "KEYCODE_PERIOD"
57 -->  "KEYCODE_ALT_LEFT"
58 -->  "KEYCODE_ALT_RIGHT"
59 -->  "KEYCODE_SHIFT_LEFT"
60 -->  "KEYCODE_SHIFT_RIGHT"
61 -->  "KEYCODE_TAB"
62 -->  "KEYCODE_SPACE"
63 -->  "KEYCODE_SYM"
64 -->  "KEYCODE_EXPLORER"
65 -->  "KEYCODE_ENVELOPE"
66 -->  "KEYCODE_ENTER"
67 -->  "KEYCODE_DEL"
68 -->  "KEYCODE_GRAVE"
69 -->  "KEYCODE_MINUS"
70 -->  "KEYCODE_EQUALS"
71 -->  "KEYCODE_LEFT_BRACKET"
72 -->  "KEYCODE_RIGHT_BRACKET"
73 -->  "KEYCODE_BACKSLASH"
74 -->  "KEYCODE_SEMICOLON"
75 -->  "KEYCODE_APOSTROPHE"
76 -->  "KEYCODE_SLASH"
77 -->  "KEYCODE_AT"
78 -->  "KEYCODE_NUM"
79 -->  "KEYCODE_HEADSETHOOK"
80 -->  "KEYCODE_FOCUS"
81 -->  "KEYCODE_PLUS"
82 -->  "KEYCODE_MENU"
83 -->  "KEYCODE_NOTIFICATION"
84 -->  "KEYCODE_SEARCH"
85 -->  "TAG_LAST_KEYCODE"


'''

def makeKeyEventPowerKey(clsvar):
    if hasattr(clsvar, "adb") :
        os.system("adb shell input keyevent POWER")
    else:
        os.system("input keyevent POWER")

def makeKeyEventVolumeUpKey(clsvar):
    if hasattr(clsvar, "adb") :
        os.system("adb shell input keyevent KEYCODE_VOLUME_UP")
    else:
        os.system("input keyevent KEYCODE_VOLUME_UP")

def makeKeyEventVolumeDownKey(clsvar):
    if hasattr(clsvar, "adb") :
        os.system("adb shell input keyevent KEYCODE_VOLUME_DOWN")
    else:
        os.system("input keyevent KEYCODE_VOLUME_DOWN")

def makeKeyEventEnterKey(clsvar):
    if hasattr(clsvar, "adb") :
        os.system("adb shell input keyevent KEYCODE_ENTER")
    else:
        os.system("input keyevent KEYCODE_ENTER")

def taskGenKeyEvent(clsvar, msg_client):

    for i in range(15) :
        makeKeyEventVolumeDownKey(clsvar)
        time.sleep(0.5)

    msgkeydown = "makeKeyEventVolumeDownKey"
    msgkeyup = "makeKeyEventVolumeUpKey"
    msgkeyenter = "makeKeyEventEnterKey"

    if hasattr(clsvar, "taskname") and  clsvar.taskname == "ref" :
        msgkeydown = "referring_" + msgkeydown
        msgkeyup = "referring_" + msgkeyup
        msgkeyenter = "referring_" + msgkeyenter

    emmcsl4a.wakeLockAcquireDim()
    while( True) :
        # makeKeyEventPowerKey(clsvar)
        # msg_client.SendMsg("makeKeyEventPowerKey ")
        # time.sleep(5)
        makeKeyEventVolumeUpKey(clsvar)
        msg_client.SendMsg(msgkeyup)
        time.sleep(7)
        makeKeyEventVolumeDownKey(clsvar)
        msg_client.SendMsg(msgkeydown)
        time.sleep(7)
        makeKeyEventEnterKey(clsvar)
        msg_client.SendMsg(msgkeyenter)
        time.sleep(7)

    emmcsl4a.wakeLockAcquireFull()
    time.sleep(5)
    emmcsl4a.wakeLockRelease()

    msg_client.SendMsg("____ finish taskGenKeyEvent, and leaving ____" )

def setpropLogService(clsvar, enable ) :
    listcmd = [ \
        " setprop persist.service.main.enable=%s",
        " setprop persist.service.system.enable=%s",
        " setprop persist.service.radio.enable=%s",
        " setprop persist.service.events.enable=%s",
        " setprop persist.service.kernel.enable=%s",
        " setprop persist.service.packet.enable=%s",
        " setprop persist.service.crash.enable=%s",
        " setprop persist.service.power.enable=%s"
        ]
    strhead = ""
    if hasattr(clsvar, "adb") :
        strhead = "adb shell "

    for cmd in listcmd :
        strcmd = strhead + cmd%enable
        os.system(strcmd)




def getSPMIValue(clsvar, attr):
    if hasattr(clsvar, "adb"):
        return os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%(attr)).readline().strip()
    else:
        return open("/sys/kernel/debug/spmi/spmi-0/%s"%(attr), "r").readline().strip()

def setSPMIValue(clsvar, attr, value):
    if hasattr(clsvar, "adb"):
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/%s" '%(value, attr))
    else:
        open("/sys/kernel/debug/spmi/spmi-0/%s"%(attr), "w").write(value)


def prepareSPMILDO20(clsvar):
    if not hasattr(clsvar, "addrSPMIEMMCVDD") :
        raise Exception("No addrSPMIEMMCVDD")
        return
    if hasattr(clsvar, "adb"):
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/address" '%(clsvar.addrSPMIEMMCVDD))
        os.system('adb shell "echo 2 > /sys/kernel/debug/spmi/spmi-0/count" ')
        values = os.popen('adb shell cat /sys/kernel/debug/spmi/spmi-0/data_raw').readline().strip()
        values = values.split()
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/save0" '%(values[0]))
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/save1" '%(values[1]))
    else:
        open("/sys/kernel/debug/spmi/spmi-0/address", "w").write(clsvar.addrSPMIEMMCVDD)
        open("/sys/kernel/debug/spmi/spmi-0/count", "w").write("2")
        values = open("/sys/kernel/debug/spmi/spmi-0/data_raw", "r").readline().strip()
        values = values.split()
        open("/sys/kernel/debug/spmi/spmi-0/save0", "w").write(values[0])
        open("/sys/kernel/debug/spmi/spmi-0/save1", "w").write(values[1])

        return values


def funcShakingSPMILDO20(clsvar ):

    if clsvar.fakewritespmi == True :
        return True
    # make loop infinite
    if hasattr(clsvar, "adb") :
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/countloop" '% clsvar.currcountLDO20shaking)
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/mtimeSleepup" '% clsvar.currmtimeSleepup)
        os.system('adb shell "echo %s > /sys/kernel/debug/spmi/spmi-0/mtimeSleepdown" '% clsvar.currmtimeSleepdown)
        os.system('adb shell "echo 0x%02x 0x%02x > /sys/kernel/debug/spmi/spmi-0/cmdloop" '% (3, clsvar.currEmmcVDD) )
        return True

    else:
        open("/sys/kernel/debug/spmi/spmi-0/countloop", "w").write("%d" % clsvar.currcountLDO20shaking )
        open("/sys/kernel/debug/spmi/spmi-0/mtimeSleepup", "w").write("%d" % clsvar.currmtimeSleepup )
        open("/sys/kernel/debug/spmi/spmi-0/mtimeSleepdown", "w").write("%d" % clsvar.currmtimeSleepdown )
        open("/sys/kernel/debug/spmi/spmi-0/cmdloop", "w").write("0x%02x 0x%02x" % (3, clsvar.currEmmcVDD))
        return True


def funcGetSPMILDO20Var(clsvar):
    if hasattr(clsvar, "adb") :
        address = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("address")).readline().strip()
        count = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("count")).readline().strip()
        data = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("data_raw")).readline().strip()
        countloop = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("countloop")).readline().strip()
        mtimeSleepup = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("mtimeSleepup")).readline().strip()
        mtimeSleepdown = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("mtimeSleepdown")).readline().strip()
        save0 = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("save0")).readline().strip()
        save1 = os.popen("adb shell cat /sys/kernel/debug/spmi/spmi-0/%s"%("save1")).readline().strip()
        return ( address, count, data, countloop, mtimeSleepup, mtimeSleepdown, save0, save1)

    else:
        address = open("/sys/kernel/debug/spmi/spmi-0/address", "r").readline().strip()
        count = open("/sys/kernel/debug/spmi/spmi-0/count", "r").readline().strip()
        data = open("/sys/kernel/debug/spmi/spmi-0/data_raw", "r").readline().strip()
        countloop = open("/sys/kernel/debug/spmi/spmi-0/countloop", "r").readline().strip()
        mtimeSleepup = open("/sys/kernel/debug/spmi/spmi-0/mtimeSleepup", "r").readline().strip()
        mtimeSleepdown = open("/sys/kernel/debug/spmi/spmi-0/mtimeSleepdown", "r").readline().strip()
        save0 = open("/sys/kernel/debug/spmi/spmi-0/save0", "r").readline().strip()
        save1 = open("/sys/kernel/debug/spmi/spmi-0/save1", "r").readline().strip()
        return ( address, count, data, countloop, mtimeSleepup, mtimeSleepdown, save0, save1)


def subtaskEmmcShakingVDD(clsvar, msg_client):

    # prepare the emmc VDD LDO20 : msleeptime : 10ms
    prepareSPMILDO20( clsvar)

    for clsvar.currEmmcVDD in clsvar.listEmmcVDD :

        for clsvar.currEmmcWriteMode in clsvar.listEmmcWriteMode:

            for clsvar.currmtimeSleepup in clsvar.listmtimeSleepup :

                for clsvar.currmtimeSleepdown in clsvar.listmtimeSleepdown :

                    for clsvar.currShakingSec in clsvar.listShakingSec :

                        msg_client.SendMsg("curr set,0x%02x,%.3f,%s,%s,%s,%s"%(clsvar.currEmmcVDD,clsvar.currEmmcVDD*0.025 + 1.5,clsvar.currEmmcWriteMode, clsvar.currmtimeSleepup, clsvar.currmtimeSleepdown, clsvar.currShakingSec))

                        msg_client.SendMsg("OnWaitRestart,set")
                        clsvar.OnWaitRestart.set()

                        ## wait for taskEmmcRandomWrite operation
                        while(emmcfunc.isWorkingFillBlockRandomAddressZero(clsvar) == False ) :
                            msg_client.SendMsg("waiting for eMMC writing")
                            time.sleep(1)
                            if clsvar.OnAllStop.is_set() == True :
                                msg_client.SendMsg("all stop signal ....")
                                return True

                        ## inner loop begining
                        sec_start = int(round(time.time()))
                        sec_end = sec_start
                        while ( (sec_end - sec_start) < clsvar.currShakingSec ):

                            if funcShakingSPMILDO20(clsvar) == False :
                                msg_client.SendMsg("fail,funcShakingSPMILDO20")
                                return False

                            ## check the return value of spmi
                            if getSPMIValue(clsvar, "result") != "0" :
                                msg_client.SendMsg("fail,spmi result")
                                return False

                            sec_end = int(round(time.time()))

                            if clsvar.OnAllStop.is_set() == True :
                                msg_client.SendMsg("all stop signal ....")
                                return True

                            time.sleep(1)

                            msg_client.SendMsg("innerloop,%s ...." % (sec_end))

                        if subtaskEmmcShakingVDD_inspect(clsvar, msg_client) == False :
                            return False

                ## Make message of emmc life
                msg_client.SendMsg("lifevalue_run,%s" % emmcfunc.getEmmcDebugfsAttrValue(clsvar, "lifevalue_run"))
                msg_client.SendMsg("BatteryValue,%s" % emmcfunc.getBatteryValue(clsvar))

    return True

def determineRebuildCRC32Table(clsvar, msg_client) :
    clsvar.currcountrebuild += 1
    msg_client.SendMsg("currcountrebuild,%s"%(clsvar.currcountrebuild))
    if ( clsvar.currcountrebuild < clsvar.intervalrebuild) :
        return True

    msg_client.SendMsg("____ beging : rebuilding CRC32Talbe ____")
    emmcfunc.setFakeEmmcWrite(clsvar, msg_client, False)
    time.sleep(60)
    emmcfunc.setFakeEmmcWrite(clsvar, msg_client, True)
    result = emmcfunc.BuildCRC32Table(clsvar, msg_client)

    msg_client.SendMsg("____ ending : rebuilding CRC32Talbe ____")
    clsvar.currcountrebuild = 0
    return result

def subtaskEmmcShakingVDD_inspect(clsvar, msg_client):

    # stop emmc write operation .
    msg_client.SendMsg("send cmdstop to 1")
    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdstop", "1" )

    # wait for emmc task sleep
    while( clsvar.OnSleepStage.is_set() == False) :
        msg_client.SendMsg("wait for emmc sleep")
        time.sleep(3)

    clsvar.OnSleepStage.clear()

    msg_client.SendMsg("before verify job")
    if emmcfunc.InspectCRC32Table(clsvar, msg_client) == False:
        msg_client.SendMsg("fail,InspectCRC32Table")
        return False
    msg_client.SendMsg("after verify job")

    return determineRebuildCRC32Table(clsvar, msg_client)

def taskEmmcShakingVDD(clsvar, msg_client):
    msg_client.SendMsg("begining,entering" )
    try:
        subtaskEmmcShakingVDD(clsvar, msg_client)
    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("error,taskEmmcShakingVDD")
        msg_client.SendMsg(msgerr)
    finally:
        funcOperCmdStop(clsvar, msg_client)
        emmcfunc.printpartitioninfo(clsvar, msg_client)
        msg_client.SendMsg("ending,leaving" )



def funcOperCmdStop(clsvar, msg_client):
    # stop emmc write operation .
    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdstop", "1" )

    # stop spmi operation.
    setSPMIValue(clsvar, "cmdstop", "1" )
    clsvar.OnAllStop.set()
    clsvar.OnWaitRestart.set()
    msg_client.SendMsg("finish setting")


def subtaskEmmcRandomWriteWithaddress(clsvar, msg_client):

    msg_client.SendMsg("begining,entering" )

    # prepare a condition for emmc writing
    clsvar.countlifemeasure = str(100)
    print (os.path.realpath("."))
    
    if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
        msg_client.SendMsg("fail,prepare the runtime Random address")
        return False
    
    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)
    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(clsvar.addrstressblock))


    # make the emmc infinite writing
    clsvar.emmccountloop = "-1"
    currEmmcWriteMode = "0"

    ret, crc32 =  emmcfunc.getcrc32ofblocks(clsvar, clsvar.addrstressblock, int(clsvar.sizetestblock))
    if ret != "0" :
        msg_client.SendMsg("fail,CRC32ed,%s,%s,%s,%s,%s"%(clsvar.addrstressblock, int(clsvar.sizetestblock),"subtask",0,ret ))

    while( True):

        msg_client.SendMsg("OnWaitRestart,waiting job")
        clsvar.OnWaitRestart.wait()

        if  clsvar.OnAllStop.is_set() == True :
            msg_client.SendMsg("OnAllStop,set,job terminating")
            break

        clsvar.OnWaitRestart.clear()

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countloop", "%s" % clsvar.emmccountloop)


        if not hasattr(clsvar, "currEmmcWriteMode") :
            clsvar.currEmmcWriteMode = clsvar.listEmmcWriteMode[0]
        
        if currEmmcWriteMode != clsvar.currEmmcWriteMode : 
            if emmcfunc.setupRandomWriteAddr( clsvar, msg_client) == False:
                return False
            currEmmcWriteMode = clsvar.currEmmcWriteMode

        msg_client.SendMsg("Before Looping in subtaskEmmcRandomWriteWithaddress ")

        ret , crc32 = emmcfunc.getcrc32ofblocks(clsvar, 0, int(clsvar.sizetestblock))
        if ret != "0" :
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(0, int(clsvar.sizetestblock),"subtask",0,ret ))

        ret , crc32 = emmcfunc.getcrc32ofblocks(clsvar, int(clsvar.sizetestblock), int(clsvar.sizetestblock))
        if ret != "0" :
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(int(clsvar.sizetestblock), int(clsvar.sizetestblock),"subtask",0,ret ))

        _ret, _crc32 =  emmcfunc.getcrc32ofblocks(clsvar, clsvar.addrstressblock, int(clsvar.sizetestblock))
        if _ret != "0" :
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(clsvar.addrstressblock, int(clsvar.sizetestblock),"subtask",0,ret ))
        elif crc32 != _crc32 :
            msg_client.SendMsg("fail,CRC32 changed")
            crc32 = _crc32
        else:
            msg_client.SendMsg("pass,CRC32 same")


        if clsvar.fakewriteemmc == False :
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "retcheck", "%s" % 1)
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", clsvar.addrstressblock )
            msg_client.SendMsg("writing,looping,addrstressblock,%s"%(clsvar.addrstressblock))
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", emmcfunc.CMD_FILLBLOCKRANDOMADDRESSZERO )
            if  emmcfunc.getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
                msg_client.SendMsg("fail,cmdeMMCTest return Failed")
        else:
            # msg_client.SendMsg("fake,stating.....")
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdindex", emmcfunc.CMD_FILLBLOCKRANDOMADDRESSZERO )
            while ( emmcfunc.getEmmcDebugfsAttrValue(clsvar, "cmdstop") != "1"):
                time.sleep(10)
                msg_client.SendMsg("fake,emmc working")
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdindex", "5000" )
            emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdstop", "0" )



        msg_client.SendMsg("After Looping in subtaskEmmcRandomWriteWithaddress ")

        # print the attribute : countrepeated
        msg_client.SendMsg("eMMC countrepeated, %s" % emmcfunc.getEmmcDebugfsAttrValue(clsvar, "countrepeated"))


        clsvar.OnSleepStage.set()
        msg_client.SendMsg("OnSleepStage,set")

    msg_client.SendMsg("ending,leaving" )

def taskEmmcRandomWriteWithaddress(clsvar, msg_client):
    msg_client.SendMsg("begining,entering" )
    try:
        subtaskEmmcRandomWriteWithaddress(clsvar, msg_client)
    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")
        msg_client.SendMsg("fail,taskEmmcRandomWriteWithaddress")
        msg_client.SendMsg(msgerr)
    finally:
        funcOperCmdStop(clsvar, msg_client)
        msg_client.SendMsg("ending,leaving" )


def makeEmmcWriteReady(clsvar, msg_client):

    # wait for emmc task sleep
    while( clsvar.OnSleepStage.is_set() == False) :
        # stop emmc write operation .
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdstop", "1" )
        msg_client.SendMsg("send cmdstop to 1")

        time.sleep(2)

    msg_client.SendMsg("OnSleepStage,clear")
    clsvar.OnSleepStage.clear()


    return True


def subtaskEmmcpoweronoff(clsvar, msg_client):

    msg_client.SendMsg("begining,entering" )



    # prepare the emmc VDD LDO20 : msleeptime : 10ms
    listvalues = prepareSPMILDO20( clsvar)
    valueson = " ".join(listvalues)
    valuesoff = " ".join([listvalues[0], "0x0"])

    clsvar.countpoweronoff = 5
    clsvar.intervalonoff = 0.005

    clsvar.listmainloop = [aa for aa in range(100)]
    clsvar.listcrc32checkloop = [aa for aa in range(1000)]

    for clsvar.currmainloop in clsvar.listmainloop :

        for clsvar.currcrc32checkloop in clsvar.listcrc32checkloop:

            for clsvar.currEmmcWriteMode in clsvar.listEmmcWriteMode :

                msg_client.SendMsg("curr set,%s,%s,%s"%(clsvar.currmainloop,clsvar.currcrc32checkloop,clsvar.currEmmcWriteMode))

                msg_client.SendMsg("OnWaitRestart,set,making eMMC Write")
                clsvar.OnWaitRestart.set()

                ## wait for subtaskEmmcRandomWrite Writing operation
                loopEmmcWritingWait = 10
                while( loopEmmcWritingWait != 0 ) :
                    msg_client.SendMsg("waiting for eMMC writing")
                    time.sleep(1)
                    if emmcfunc.isWorkingFillBlockRandomAddressZero(clsvar) == True :
                        break
                    if clsvar.OnAllStop.is_set() == True :
                        msg_client.SendMsg("OnAllStop,set,all stop signal ....")
                        return True
                    loopEmmcWritingWait -= 1

                if  loopEmmcWritingWait == 0 :
                    msg_client.SendMsg("fail,fail for emmcwriting")
                else:
                    msg_client.SendMsg("ready to power on/off")
                    time.sleep(1)

                    for currpoweronoff in range(clsvar.countpoweronoff) :
                        setSPMIValue(clsvar, "data", valuesoff)
                        time.sleep(clsvar.intervalonoff)
                        setSPMIValue(clsvar, "data", valueson)
                        msg_client.SendMsg("after the spmi power offon")

                        # emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countloop", 1 )
                        # emmcfunc.setEmmcDebugfsAttrValue(clsvar, "param2", 0 ) # 0 : mmc_power_cycle
                        # emmcfunc.setEmmcDebugfsAttrValue(clsvar, "param1", 1 ) # ms delay time
                        # emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", 4 )
                        #
                        # msg_client.SendMsg("after the reset eMMC")

                        time.sleep(3)

                    msg_client.SendMsg("after the loop of power on/off")


                if clsvar.OnAllStop.is_set() == True :
                    msg_client.SendMsg("OnAllStop,set,job terminating")
                    return True

                makeEmmcWriteReady(clsvar, msg_client)

        msg_client.SendMsg("log,before verify job")
        if emmcfunc.InspectCRC32Table(clsvar, msg_client) == False:
            msg_client.SendMsg("fail,InspectCRC32Table")
            return False
        msg_client.SendMsg("log,after verify job")

        ## Make message of emmc life
        msg_client.SendMsg("lifevalue_run,%s" % emmcfunc.getEmmcDebugfsAttrValue(clsvar, "lifevalue_run"))
        msg_client.SendMsg("BatteryValue,%s" % emmcfunc.getBatteryValue(clsvar))

    msg_client.SendMsg("ending,leaving" )
    return True


def taskEmmcpoweronoff(clsvar, msg_client):
    msg_client.SendMsg("begining,entering" )
    try:
        subtaskEmmcpoweronoff(clsvar, msg_client)
    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("error,taskEmmcpoweronoff")
        msg_client.SendMsg(msgerr)
    finally:
        funcOperCmdStop(clsvar, msg_client)
        emmcfunc.printpartitioninfo(clsvar, msg_client)
        msg_client.SendMsg("ending,leaving" )


def scenario_poweronoff(clsvar, msg_client) :

    msg_client.SendMsg("begining,entering" )

    sec_start = int(round(time.time()))

    ## ______________ setup of test environment   __________________
    clsvar.OnAllStop = emmcfunc.OnAllStop(clsvar)
    clsvar.OnWaitRestart = emmcfunc.OnWaitRestart(clsvar)
    clsvar.OnSleepStage = emmcfunc.OnSleepStage(clsvar)

    clsvar.OnAllStop.clear()
    clsvar.OnWaitRestart.clear()
    clsvar.OnSleepStage.clear()

    clsvar.fakewriteemmc = False
    clsvar.fakewritespmi = False

    # clsvar.currcountLDO20shaking = 1000
    # clsvar.listmtimeSleepup = [10,20]
    # clsvar.listmtimeSleepdown = [10,20]
    # clsvar.listEmmcVDD = [aa for aa in range(50, 46, -1)]
    # clsvar.listShakingSec = [150]


    clsvar.listEmmcWriteMode = [ "random", "sequence"]
    clsvar.currEmmcWriteMode = "random"

    if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
        msg_client.SendMsg("fail,prepare the runtime Random address")
        raise  Exception("No runtime Random address")
        return False


    listtask = []


    ## ______________ make the worker process :emmcwrite   __________________
    runnerEmmc = Process( target=taskEmmcRandomWriteWithaddress, args=(clsvar,msg_client,))
    runnerEmmc.start()
    listtask.append(runnerEmmc)


    ## ______________ make the worker process :shakingVDD   __________________
    runnerpoweronoff = Process( target=taskEmmcpoweronoff, args=(clsvar,msg_client,))
    runnerpoweronoff.start()
    listtask.append(runnerpoweronoff)

    while True :
        if (runnerpoweronoff.is_alive() == True ) and (runnerEmmc.is_alive() == True):
            msg_client.SendMsg("main function,sleeping ...")
            time.sleep(60)

            continue
        else:
            break

    clsvar.OnAllStop.set()
    for task in listtask :
        task.terminate()
        task.join()

    msg_client.SendMsg("stop all process")


    sec_diff = int(round(time.time())) - sec_start
    msg_client.SendMsg("collapsed time,%s"%(timedelta(seconds = sec_diff)))

    msg_client.SendMsg("ending,leaving" )

def scenario_sleepwake(clsvar, msg_client) :

    msg_client.SendMsg("begining,entering" )

    try:
        # emmcfunc.disableChargingEvent(clsvar, False)
        # emmcfunc.disableChargingEvent(clsvar, True)
        clsvar.countlifemeasure = str(100)

        if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
            msg_client.SendMsg("fail,prepare the runtime Random address")
            raise  Exception("No runtime Random address")
            return False

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(clsvar.addrstressblock))

        sec_start = int(round(time.time()))

        clsvar.listtaskloop = [aa for aa in range(40)]
        clsvar.listEmmcWriteMode = [ "random","sequence" ]
        clsvar.listEmmcWriteSize = [10]
        # clsvar.listPreSleepSec = [ 0,5, 10, 15, 20, 25,30]
        clsvar.listdeepsleepcount = [aa for aa in range(100)]

        if not hasattr(clsvar, "deepsleepsec") or clsvar.deepsleepsec == None :
            clsvar.deepsleepsec = 10

        msg_client.SendMsg("deepsleepsec,%s"%clsvar.deepsleepsec)

        clsvar.currPreSleepSec = 1

        clsdeepsleep = emmcfunc.DeepSleepWake()
        countdeepsleepprev = emmcfunc.getDeepSleepCount(clsvar)

        for clsvar.currtaskloop in clsvar.listtaskloop :

            for clsvar.currEmmcWriteMode   in clsvar.listEmmcWriteMode :

                if emmcfunc.setupRandomWriteAddr( clsvar, msg_client) == False:
                    return False

                for clsvar.currEmmcWriteSize in clsvar.listEmmcWriteSize :

                    msg_client.SendMsg("curr set,%s,%s,%s,%s"%(clsvar.currtaskloop,clsvar.currEmmcWriteMode,clsvar.currEmmcWriteSize,clsvar.currPreSleepSec))

                    for  clsvar.currdeepsleepcount  in  clsvar.listdeepsleepcount :

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

                    msg_client.SendMsg("log,before verify job")
                    if emmcfunc.InspectCRC32Table(clsvar, msg_client) == False:
                        msg_client.SendMsg("fail,InspectCRC32Table")
                        return False
                    msg_client.SendMsg("log,after verify job")


        sec_diff = int(round(time.time())) - sec_start
        msg_client.SendMsg("collapsed time,%s"%(timedelta(seconds = sec_diff)))

        # emmcfunc.disableChargingEvent(clsvar, False)
    #
    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("fail,scenario_sleepwake")
        msg_client.SendMsg(msgerr)

    msg_client.SendMsg("ending,leaving" )

def scenario_sleepwakeCRC32not(clsvar, msg_client) :

    msg_client.SendMsg("begining,entering" )

    try:
        # open and read the fail emmcblock address
        listreadblockaddress = []
        for line in  open("crc32not.list") :
            listitem = line.split(",")
            if len(listitem) > 7  and clsvar.DeviceSerialNo in listitem[2] :
                listreadblockaddress.append(listitem[7])


        # emmcfunc.disableChargingEvent(clsvar, False)
        # emmcfunc.disableChargingEvent(clsvar, True)
        clsvar.countlifemeasure = str(100)

        if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
            msg_client.SendMsg("fail,prepare the runtime Random address")
            raise  Exception("No runtime Random address")
            return False

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(clsvar.addrstressblock))

        sec_start = int(round(time.time()))

        clsvar.listtaskloop = [aa for aa in range(40)]
        clsvar.listEmmcWriteMode = [ "random","sequence" ]
        clsvar.listEmmcWriteSize = [10]
        # clsvar.listPreSleepSec = [ 0,5, 10, 15, 20, 25,30]
        clsvar.listdeepsleepcount = [aa for aa in range(100)]

        if not hasattr(clsvar, "deepsleepsec") or clsvar.deepsleepsec == None :
            clsvar.deepsleepsec = 10

        msg_client.SendMsg("deepsleepsec,%s"%clsvar.deepsleepsec)

        clsvar.currPreSleepSec = 1

        clsdeepsleep = emmcfunc.DeepSleepWake()
        countdeepsleepprev = emmcfunc.getDeepSleepCount(clsvar)

        for clsvar.currtaskloop in clsvar.listtaskloop :

            for clsvar.currEmmcWriteMode   in clsvar.listEmmcWriteMode :

                if emmcfunc.setupRandomWriteAddr( clsvar, msg_client) == False:
                    return False

                for clsvar.currEmmcWriteSize in clsvar.listEmmcWriteSize :

                    msg_client.SendMsg("curr set,%s,%s,%s,%s"%(clsvar.currtaskloop,clsvar.currEmmcWriteMode,clsvar.currEmmcWriteSize,clsvar.currPreSleepSec))

                    for  clsvar.currdeepsleepcount  in  clsvar.listdeepsleepcount :

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

                        if  emmcfunc.getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
                            msg_client.SendMsg("fail,EmmcWriteError")

                    msg_client.SendMsg("log,before crc32not")
                    for start in listreadblockaddress :
                        ret, crc32 =  emmcfunc.getcrc32ofblocks(clsvar, start, clsvar.sizetestblock)
                        if ret != "0" :
                            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, clsvar.sizetestblock,"wholearea","pos_na",ret ))
                    msg_client.SendMsg("log,after crc32not")


        sec_diff = int(round(time.time())) - sec_start
        msg_client.SendMsg("collapsed time,%s"%(timedelta(seconds = sec_diff)))

        # emmcfunc.disableChargingEvent(clsvar, False)
    #
    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("fail,scenario_sleepwake")
        msg_client.SendMsg(msgerr)

    msg_client.SendMsg("ending,leaving" )

def scenario_referring(clsvar, msg_client) :

    msg_client.SendMsg("begining,entering" )

    loop = 24 * 7
    while(loop != 0 ):
        time.sleep(3600)

        msg_client.SendMsg ("main before InspectCRC32Table" )
        result = emmcfunc.InspectCRC32Table(clsvar, msg_client)
        if result == False :
            msg_client.SendMsg("fail, InspectCRC32Table")
            exit()

        loop -= 1

    msg_client.SendMsg("ending,leaving" )

def scenario_keepread(clsvar, msg_client) :
    msg_client.SendMsg("begining,entering" )

    try:
        clsvar.countlifemeasure = str(100)

        if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
            msg_client.SendMsg("fail,prepare the runtime Random address")
            raise  Exception("No runtime Random address")
            return False

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(clsvar.addrstressblock))


        clsvar.listtaskloop = [aa for aa in range(10000)]
        clsvar.listinnerloop = [aa for aa in range(10000)]

        start = clsvar.addrstressblock
        size = 8

        ret, crc32 = emmcfunc.getcrc32ofblocks(clsvar, start, size )
        if ret != "0" :
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, size,"task","pos_na",ret ))
            return
        prevcrc32 = crc32

        for clsvar.currtaskloop in clsvar.listtaskloop :
            msg_client.SendMsg("currtaskloop,%s"%(clsvar.currtaskloop))
            for clsvar.currinnerloop in clsvar.listinnerloop :
                ret, crc32 = emmcfunc.getcrc32ofblocks(clsvar, start, size )
                if ret != "0" :
                    msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, size,"task","pos_na",ret ))
                    continue
                if crc32 != prevcrc32 :
                    msg_client.SendMsg("fail,crc23 changed,%s"%(crc32))
                    prevcrc32 = crc32
                    continue

            msg_client.SendMsg("log,before verify job")
            if emmcfunc.InspectCRC32Table(clsvar, msg_client) == False:
                msg_client.SendMsg("fail,InspectCRC32Table")
                return False
            msg_client.SendMsg("log,after verify job")


    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("fail,scenario_keepread")
        msg_client.SendMsg(msgerr)

    msg_client.SendMsg("ending,leaving" )

def scenario_keepwrite(clsvar, msg_client) :
    msg_client.SendMsg("begining,entering" )
    try:
        clsvar.countlifemeasure = str(100)

        if emmcfunc.makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client) == False :
            msg_client.SendMsg("fail,prepare the runtime Random address")
            raise  Exception("No runtime Random address")
            return False

        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countlifemeasure", clsvar.countlifemeasure)
        emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(clsvar.addrstressblock))


        clsvar.listtaskloop = [aa for aa in range(10000)]
        clsvar.listinnerloop = [aa for aa in range(100)]
        clsvar.listwriteloop = [aa for aa in range(100)]

        start = clsvar.addrstressblock
        size = 8192

        ret, crc32 = emmcfunc.getcrc32ofblocks(clsvar, start, size )
        if ret != "0" :
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, size,"task","pos_na",ret ))
            return
        prevcrc32 = crc32

        clsvar.currEmmcWriteMode = "random"
        clsvar.currEmmcWriteSize = 10
        if emmcfunc.setupRandomWriteAddr( clsvar, msg_client) == False:
            return False

        for clsvar.currtaskloop in clsvar.listtaskloop :

            for clsvar.currinnerloop in clsvar.listinnerloop :
                msg_client.SendMsg("currtaskloop,%s,currinnerloop,%s"%(clsvar.currtaskloop, clsvar.currinnerloop))
                for clsvar.currwriteloop in clsvar.listwriteloop :

                    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "countloop", "%s" % clsvar.currEmmcWriteSize)
                    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "retcheck", "%s" % 1)
                    # assign  clsvar.addrstressblock to addrblockstart
                    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "addrblockstart", clsvar.addrstressblock )
                    emmcfunc.setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", emmcfunc.CMD_FILLBLOCKRANDOMADDRESSZERO )

                    if  emmcfunc.getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
                        msg_client.SendMsg("fail,EmmcWriteError,currwriteloop,%s"%(clsvar.currwriteloop))

                # check if crc32 is changed
                ret, crc32 = emmcfunc.getcrc32ofblocks(clsvar, start, size )
                if ret != "0" :
                    msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, size,"task","pos_na",ret ))

                elif crc32 != prevcrc32 :
                    msg_client.SendMsg("fail,crc23 changed,%s"%(crc32))
                    prevcrc32 = crc32

                msg_client.SendMsg("emmclife,%s"%( emmcfunc.getEmmcLifeValueofext_csd(clsvar) ))

            msg_client.SendMsg("log,before verify job")
            if emmcfunc.InspectCRC32Table(clsvar, msg_client) == False:
                msg_client.SendMsg("fail,InspectCRC32Table")
                return False
            msg_client.SendMsg("log,after verify job")

    except Exception as e:
        import traceback
        msgerr = traceback.format_exc()
        msgerr = msgerr.replace("\n", "$")

        ## replace the "\n" with "$"
        msg_client.SendMsg("fail,scenario_keepwrite")
        msg_client.SendMsg(msgerr)

    msg_client.SendMsg("ending,leaving" )

