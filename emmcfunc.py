# -*- coding: utf-8 -*-
from __future__ import print_function
import random
import sys


__author__ = 'jaehyek.choi'

"""
purpose :

"""

import subprocess

import os
from datetime import datetime, timedelta
import time

# import fcntl

from struct import *

class clsVariables ():
    def __init__(self):
        # self.__dict__["pathmmc"] = "/sys/kernel/debug/mmc0/mmc0:0001"
        if sys.platform == "win32":
            self.__dict__["adb"] = True

        self.__dict__["pathmmc"] = getEmmcPath(self)

    def __str__(self):
        temp = ""
        for nameattr in self.__dict__ :
            temp += nameattr + ":" + self.__dict__[nameattr] + "\n"
        return temp

'''
format for struct.pack
Character Byte-order            Size        Alignment
-----------------------------------------------------------
@       native                  native      native
=       native                  standard    none
<       little-endian           standard    none
>       big-endian              standard    none
!       network (= big-endian)  standard    none


Format  C-Type          Python-type         Standard-size Notes
-----------------------------------------------------------------------
x       pad byte        no value
c       char            string of length 1  1
b       signed char     integer             1               (3)
B       unsigned char   integer             1               (3)
?       _Bool           bool                1               (1)
h       short           integer             2               (3)
H       unsigned short  integer             2               (3)
i       int             integer             4               (3)
I       unsigned int    integer             4               (3)
l       long            integer             4               (3)
L       unsigned long   integer             4               (3)
q       long long       integer             8               (2), (3)
Q       unsigned long long integer          8               (2), (3)
f       float           float               4               (4)
d       double          float               8               (4)
s       char[]          string
p       char[]          string
P       void *          integer   (5), (3)

'''


'''
struct rtc_time {
	int tm_sec;
	int tm_min;
	int tm_hour;
	int tm_mday;
	int tm_mon;
	int tm_year;
	int tm_wday;
	int tm_yday;
	int tm_isdst;
};

struct rtc_wkalrm {
	unsigned char enabled;	/* 0 = alarm disabled, 1 = alarm enabled */
	unsigned char pending;  /* 0 = alarm not pending, 1 = alarm pending */
	struct rtc_time time;	/* time the alarm is set to */
};

#define RTC_RD_TIME	    _IOR('p', 0x09, struct rtc_time) /* Read RTC time   */
#define RTC_SET_TIME	_IOW('p', 0x0a, struct rtc_time) /* Set RTC time    */
#define RTC_WKALM_SET	_IOW('p', 0x0f, struct rtc_wkalrm)/* Set wakeup alarm*/
#define RTC_WKALM_RD	_IOR('p', 0x10, struct rtc_wkalrm)/* Get wakeup alarm*/


'''

"""
Linux ioctl numbers made easy
size can be an integer or format string compatible with struct module
for example include/linux/watchdog.h:

#define WATCHDOG_IOCTL_BASE     'W'
struct watchdog_info {
        __u32 options;          /* Options the card/driver supports */
        __u32 firmware_version; /* Firmware version of the card */
        __u8  identity[32];     /* Identity of the board */
};

#define WDIOC_GETSUPPORT  _IOR(WATCHDOG_IOCTL_BASE, 0, struct watchdog_info)
becomes:

WDIOC_GETSUPPORT = _IOR(ord('W'), 0, "=II32s")


"""
import struct
# constant for linux portability
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8

# architecture specific
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRMASK = (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK = (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2


def _IOC(dir, type, nr, size):
    if isinstance(size, str) :
        size = struct.calcsize(size)
    return dir  << _IOC_DIRSHIFT  | \
           type << _IOC_TYPESHIFT | \
           nr   << _IOC_NRSHIFT   | \
           size << _IOC_SIZESHIFT


def _IO(type, nr): return _IOC(_IOC_NONE, type, nr, 0)
def _IOR(type, nr, size): return _IOC(_IOC_READ, type, nr, size)
def _IOW(type, nr, size): return _IOC(_IOC_WRITE, type, nr, size)
def _IOWR(type, nr, size): return _IOC(_IOC_READ | _IOC_WRITE, type, nr, size)

## _____  for /dev/rtc0  _____________________________________________________________________________

SIZE_STRUCT_RTC_TIME = 4 * 9
SIZE_STRUCT_RTC_WKALAM = SIZE_STRUCT_RTC_TIME  + 2

# RTC_RD_TIME = _IOR(ord('p'), 9, SIZE_STRUCT_RTC_TIME )
# RTC_SET_TIME = _IOW(ord('p'), 10, SIZE_STRUCT_RTC_TIME )

# RTC_ALM_SET	_IOW(ord('p'), 0x07, SIZE_STRUCT_RTC_TIME)
# RTC_ALM_READ	_IOR(ord('p'), 0x08, SIZE_STRUCT_RTC_TIME)
#
# RTC_WKALM_SET = _IOW(ord('p'), 15, SIZE_STRUCT_RTC_WKALAM )
# RTC_WKALM_RD = _IOR(ord('p'), 16, SIZE_STRUCT_RTC_WKALAM )
# RTC_DEVICE_UP	_IOW(ord('p'), 0x13, SIZE_STRUCT_RTC_WKALAM)


RTC_ALM_READ    =0x80247008
RTC_ALM_SET     =0x40247007
RTC_RD_TIME     =0x80247009
RTC_SET_TIME    =0x4024700a
RTC_WKALM_SET   =0x4028700f
RTC_WKALM_RD    =0x80287010
RTC_AIE_ON      =0x7001
RTC_AIE_OFF     =0x7002

#
# class RTCTimer():
#     def __init__(self):
#         self.rtcdevice = "/dev/rtc0"
#
#     def getNowTM(self):
#         timenow = int(round(time.time() * 1000))
#         listdatetime = ConvertTimeStampToString(timenow, "%Y,%m,%d,%H,%M,%S").split(",")
#         tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = tuple(listdatetime)
#
#         tm_year = int(tm_year)
#         tm_mon = int(tm_mon)
#         tm_mday = int(tm_mday)
#         tm_hour = int(tm_hour)
#         tm_min = int(tm_min)
#         tm_sec = int(tm_sec)
#
#         tm_mon -= 1
#         tm_year -= 1900
#         return (tm_sec, tm_min, tm_hour, tm_mday, tm_mon, tm_year )
#
#     def setRTCTime(self, rtc_time):
#         sec, min, hour, mday, mon, year = rtc_time
#         indata = struct.pack("=9i",sec, min, hour, mday, mon, year, 0,0,0)
#
#         f = open(self.rtcdevice, "w")
#         fcntl.ioctl(f.fileno(), RTC_SET_TIME, indata)
#         f.close()
#
#     def getRTCTime(self):
#         indata = struct.pack("=9I",0, 0, 0, 0, 0, 0, 0,0,0)
#
#         f = open(self.rtcdevice, "rb")
#         outdata = fcntl.ioctl(f.fileno(), RTC_RD_TIME, indata)
#         f.close()
#
#         rtc_time = struct.unpack("=9I", outdata)
#         return rtc_time
#
#     def setRTCAlarm(self, rtc_wkalrm):
#         indata = struct.pack("=HH9I",rtc_wkalrm[0],rtc_wkalrm[1],rtc_wkalrm[2],rtc_wkalrm[3],rtc_wkalrm[4],rtc_wkalrm[5],rtc_wkalrm[6],rtc_wkalrm[7],rtc_wkalrm[8],rtc_wkalrm[9],rtc_wkalrm[10])
#
#         f = open(self.rtcdevice, "wb")
#         fcntl.ioctl(f.fileno(), RTC_AIE_ON )
#         fcntl.ioctl(f.fileno(), RTC_WKALM_SET , indata)
#         f.close()
#
#     def getRTCAlarm(self):
#
#         indata = struct.pack("=HH9I", 0,0, 0,0,0, 0,0,0, 0,0,0)
#         f = open(self.rtcdevice, "rb")
#         outdata =  fcntl.ioctl(f.fileno(), RTC_WKALM_RD, indata)
#         f.close()
#
#         rtc_wkalrm = struct.unpack("=HH9I", outdata)
#
#         return rtc_wkalrm
#
#


## _____  for /dev/alarm  _____________________________________________________________________________
'''
struct timespec {
        long       ts_sec;
        long       ts_nsec;
};
'''
SIZE_STRUCT_TIMESPEC = 4 * 2

# def ALARM_IOW(c, type, size)  :  return   _IOW(ord('a'), (c) | ((type) << 4), size)
# def ANDROID_ALARM_SET(type)   :  return   ALARM_IOW(2, type, SIZE_STRUCT_TIMESPEC)
# def ANDROID_ALARM_SET_AND_WAIT(type) :  return  ALARM_IOW(3, type, SIZE_STRUCT_TIMESPEC)
# def ANDROID_ALARM_GET_TIME(type) :      return  ALARM_IOW(4, type, SIZE_STRUCT_TIMESPEC)
# def ANDROID_ALARM_SET_RTC() :           return  _IOW(ord('a'), 5, SIZE_STRUCT_TIMESPEC)

# alarm type
ALARM_type_RTC_WAKEUP = 0 << 4
ALARM_type_RTC = 1 << 4
ALARM_type_ELAPSED_REALTIME_WAKEUP = 2 << 4
ALARM_type_ELAPSED_REALTIME = 3 << 4
ALARM_type_RTC_POWEROFF_WAKEUP = 4 << 4
ALARM_type_SYSTEMTIME = 5 << 4
ALARM_type_TYPE_COUNT = 6 << 4

# alarm command
ALARM_cmd_CLEAR = 0x6100
ALARM_cmd_SET_AND_WAIT = 0x40086103
ALARM_cmd_SET = 0x40086102
ALARM_cmd_WAIT = 0x6101
ALARM_cmd_SET_RTC = 0x40086105
ALARM_cmd_GET_TIME = 0x40086104

#현재 관측된 명령들.
ANDROID_ALARM_GET_ELAPSED_REALTIME = 0x40086134
ANDROID_ALARM_SET_ELAPSED_REALTIME_WAKEUP =  0x40086122
ANDROID_ALARM_SET_ELAPSED_REALTIME =  0x40086132
ANDROID_ALARM_WAIT = 0x6101

## _______________ _____________________________________________________________________________

# class Alarm():
#     def __init__(self):
#         self.rtcdevice = "/dev/alarm"
#
#     def getRTCTime(self):
#         indata = struct.pack("=LL",0, 0)
#         f = open(self.rtcdevice, "w")
#         outdata =  fcntl.ioctl(f.fileno(), ALARM_cmd_GET_TIME + ALARM_type_ELAPSED_REALTIME, indata)
#         f.close()
#         timespec = struct.unpack("=LL", outdata)
#         return  timespec
#
#     def setRTCTimeWait(self,timespec):
#         indata = struct.pack("=LL",timespec[0], timespec[1])
#         f = open(self.rtcdevice, "w")
#         fcntl.ioctl(f.fileno(), ALARM_cmd_SET_AND_WAIT + ALARM_type_ELAPSED_REALTIME_WAKEUP, indata)
#         f.close()
#
#     def sleep(self, sec ):
#
#         timespec = self.getRTCTime()
#         timespec = list(timespec)
#         timespec[0] += sec
#         self.setRTCTimeWait(timespec)
#

def setFakeEmmcWrite(clsvar,msg_client, enable) :

    if not hasattr(clsvar, "EnableFakeEmmcWrite") :
        return

    if clsvar.EnableFakeEmmcWrite == True :
        if enable == True :
            setEmmcDebugfsAttrValue(clsvar, "taskop", 1)
            msg_client.SendMsg("Enable Emmc Fake Write")
        else:
            setEmmcDebugfsAttrValue(clsvar, "taskop", 0)
            msg_client.SendMsg("Disable Emmc Fake Write")


def disableChargingEvent(clsvar, disable):
    if not hasattr(clsvar, "modelname") :
        raise Exception("disableChargingEvent : No Model name")

    if clsvar.modelname == "LG-D855" :
        fileevent = "/sys/class/power_supply/battery/charger_sleep_enable"

    elif clsvar.modelname in ["LG-F470L","LG-V700" ]  :
        fileevent = "/sys/module/qpnp_charger/parameters/qpnp_sleep_enable"

    elif clsvar.modelname == "LG-H440n" :
        fileevent = "/sys/module/qpnp_linear_charger/parameters/qpnp_sleep_enable"

    elif clsvar.modelname == "LG-F600L" :
        fileevent = "/sys/class/power_supply/battery/charging_enabled"

        f = open(fileevent, "w")
        if disable == True :
            f.write("0")
            f.close()
        else:
            f.write("1")
            f.close()

        strcmd = "cat " + fileevent
        strret = os.popen(strcmd).readline()

        print("charging_enabled,%s"%strret)

        return True

    else:
        raise Exception("disableChargingEvent : No Model name")

    try :
        if disable == True :
            open(fileevent, "w").write("1")
        else:
            open(fileevent, "w").write("0")
        return True
    except :
        return False




class DeepSleepWake():
    def __init__(self) :
        fileprefer = "/data/data/com.lge.emmctest/"


        if  os.path.exists(fileprefer) == False :
            raise Exception("No eMMCTest.apk")

    def sleep(self, sec):
        # if sec <= 10 :
        #     sec = 10
        # elif sec <= 20 :
        #     sec = 20
        # else:
        #     sec = 30

        adbcmd = "am broadcast -a com.lge.emmctest.TEST_START_ACTION --include-stopped-packages "
        adbcmd += " --ez sleepwakeup true "
        adbcmd += " --ez randomwrite  false "
        adbcmd += " --ez sequentialwrite  false "
        adbcmd += " --ez swreset   false "
        adbcmd += " --el sleep_time  %s "
        adbcmd += " --el wakeup_time  5 "
        adbcmd += " --el repeat 1 "

        cmd = adbcmd%(sec)

        os.system(cmd)
        time.sleep(10)


CMD_SEQUENCEWRITE = "0"
CMD_RANDOMWRITE = "1"
CMD_NOTSAVEWRITE = "2"
CMD_NOTSAVERANDOM = "3"

CMD_POWERONOFFREPEAT = "4"
CMD_POWERONOFFREPEATNOSAVING = "5"
CMD_SLEEPWAKE = "6"
CMD_FLUSHCACHE = "7"

CMD_ENDISABLECACHE = "8"
CMD_MODIFYEXTCSD = "9"
CMD_SETIOS = "10"
CMD_FILLBLOCKADDRESSZERO = "11"

CMD_FILLBLOCKRANDOMADDRESSZERO = "12"
CMD_CRCCHECK = "13"
CMD_ERASEBLOCK = "14"
CMD_KILLPID = "15"

JOB_NOTHING	 = 5000
SIZEADDRRANDOM = 1024

'''
--- job definition ---
0:      Multi-block sequence write( save blocks)
1:      Multi-block random write( save blocks)
2:      Multi-block size write(not save blocks)
3:      Multi-block random write(not save blocks)
4:      eMMC Power On/Off repeat
5:      eMMC Power On/Off repeat without restoring
6:      eMMC Sleep and wakeup
7:      eMMC Flush Cache
8:      eMMC enable/disable Cache
9:      eMMC Modify EXT_CSD value
10:     eMMC Do Set IOS
11:     eMMC fill block out with address or zero
12:     Multi-block random write with address or zero(not save blocks)
13:     Multi-block CRC32 check
14:     Multi-block Erase
15:     kill pid

'''

def ConvertTimeStampToString ( timestampmilisecond , strformat=""):
    if timestampmilisecond == None:
        return ""
    strfmt = "%Y-%m-%d %H:%M:%S"
    if len(strformat) > 0 :
        strfmt = strformat
    outdatetime = datetime(1970, 1, 1) + timedelta(hours= 9, milliseconds=timestampmilisecond)
    return outdatetime.strftime(strfmt)

def ConvertDateTimeToMiliSeconds( y, m, d, h = 0 , minute = 0 , s = 0 ):
    daydiff = datetime(y, m, d, h, minute, s) - datetime(1970, 1, 1, 9, 0, 0)
    return int(daydiff.total_seconds()) * 1000
'''
print (ConvertTimeStampToString(1340751010888))
print (ConvertDateTimeToMiliSeconds(2012, 6, 26, 22, 50, 10))
exit()
--> result---
2012-06-26 22:50:10
1340751010000

'''




def makeRandomtxt(count, nameoutfile):
    listitems = range(count * 2 )
    random.shuffle(listitems)
    del listitems[count:]
    for i in range(count) :
        listitems[i] = "%08x"%(listitems[i] * 16)

    f = open(nameoutfile, "w")
    f.write(",".join(listitems))
    f.close()



def convertToRandomBin(nameinfile, nameoutfile):
    #read random integer list
    listitems = open(nameinfile).readline().split(",")
    sizebackupbuffer = len(listitems)
    for i in range(sizebackupbuffer) :
        listitems[i] = int(listitems[i], 16)

    f = open(nameoutfile, "wb")
    for i in range(sizebackupbuffer):
        f.write(pack("l",listitems[i]  ))

    f.close()




def getDeepSleepCount(clsvar):

    strcmd = "cat /sys/kernel/debug/rpm_stats"
    if hasattr(clsvar, "adb"):
        strcmd = "adb shell  " + strcmd

    deepsleepcount = 0
    strret = os.popen(strcmd).readlines()

    strtag = "reserved"
    if clsvar.modelname == "LG-F600L" :
        strtag = "reserved[1]"


    for line in strret :
        if strtag in line :
            deepsleepcount = line.split(":")[1].strip()
            break

    return int(deepsleepcount)


def getScreenSize(clsvar):
    strcmd = 'dumpsys window | grep "mUnrestrictedScreen" '
    if hasattr(clsvar, "adb"):
        strcmd = "adb shell  " + strcmd

    # mUnrestrictedScreen=(0,0) 720x1280
    screensize = os.popen(strcmd).readline()
    screensize = screensize.split(" ")[-1]

    listscreensize = screensize.split('x')
    return int(listscreensize[0]),int(listscreensize[1])

def getModelName(clsvar):
    if hasattr(clsvar, "adb"):
        return os.popen("adb shell getprop ro.product.model").readline().strip()
    else:
        return os.popen("getprop ro.product.model").readline().strip()

def getDeviceSerialNo(clsvar):
    if hasattr(clsvar, "adb"):
        return os.popen("adb shell getprop ro.serialno").readline().strip()
    else:
        return os.popen("getprop ro.serialno").readline().strip()

def getBoardName(clsvar):
    if hasattr(clsvar, "adb"):
        return os.popen("adb shell getprop ro.product.board").readline().strip()
    else:
        return os.popen("getprop ro.product.board").readline().strip()

def getEmmcGBSize(clsvar):
    strcmd = "cat /sys/block/mmcblk0/size"
    if hasattr(clsvar, "adb"):
        strcmd = "adb shell  " + strcmd

    strret = os.popen(strcmd).readline().strip()
    ret =   int ( int(strret) * 512 / 1024 / 1024/ 1024)

    return  int((ret + 4 ) / 4) * 4

def getEmmcPath(clsvar):
    strcmd = "ls -al /sys/block/mmcblk0/device"
    if hasattr(clsvar, "adb"):
        strcmd = "adb shell  " + strcmd

    strret = os.popen(strcmd).readline().strip().split("/")[-1]
    devno = strret.split(":")[0]
    ret = "/sys/kernel/debug/mmc0/mmc0:0001"
    if devno == "mmc1" :
        ret = "/sys/kernel/debug/mmc1/mmc1:0001"
    return  ret

def getAddrSPMIEMMCVDD(clsvar):

    if hasattr(clsvar, "addrSPMIEMMCVDD") and clsvar.addrSPMIEMMCVDD != None :
        return clsvar.addrSPMIEMMCVDD

    boardname = getBoardName(clsvar)
    if boardname in["MSM8974","msm8992" ] :
        return "0x15340"
    elif boardname == "MSM8226" :
        return "0x15040"
    elif boardname == "msm8916" :
        return "0x14A40"
    else:
        raise Exception("Unknown Board")

def getBatteryValue(clsvar):
    if hasattr(clsvar, "adb"):
        return os.popen("adb shell cat /sys/class/power_supply/battery/capacity").readline().strip()
    else:
        return open("/sys/class/power_supply/battery/capacity").readline().strip()

def getEmmcDebugfsAttrValue(clsvar, attr):
    if hasattr(clsvar, "pathmmc"):
        if hasattr(clsvar, "adb"):
            return os.popen("adb shell cat %s/%s"% (clsvar.pathmmc, attr)).readline().strip()
        else:
            return open("%s/%s"%(clsvar.pathmmc ,attr)).readline().strip()
    else:
        print ("No attribtue and Getting")
        return ""

def getEmmcDebugfsAttrValueLines(clsvar, attr):
    if hasattr(clsvar, "pathmmc"):
        if hasattr(clsvar, "adb"):
            return os.popen("adb shell cat %s/%s"% (clsvar.pathmmc, attr)).readlines()
        else:
            return open("%s/%s"%(clsvar.pathmmc ,attr)).readlines()
    else:
        print ("No attribtue and Getting")
        return []

def setEmmcDebugfsAttrValue(clsvar, attr, value):
    if hasattr(clsvar, "pathmmc"):
        if hasattr(clsvar, "adb"):
            os.system('adb  shell "echo %s > %s/%s " '% (value, clsvar.pathmmc, attr ))
        else:
            open("%s/%s"%(clsvar.pathmmc ,attr), "w").write("%s"% value )
    else:
        print ("No attribtue and Setting")



def optimizesizebackupbuffer(clsvar ):
    sizebackupbuffer = int(clsvar.sizebackupbuffer)
    while(sizebackupbuffer> 0 ) :
        setEmmcDebugfsAttrValue(clsvar, "sizebackupbuffer", str(sizebackupbuffer))
        attrvalue = getEmmcDebugfsAttrValue(clsvar, "sizebackupbuffer")

        if sizebackupbuffer == int( attrvalue ) :
            break
        sizebackupbuffer -= 1

    clsvar.sizebackupbuffer = str(sizebackupbuffer)
    print ("sizebackupbuffer : %s " % clsvar.sizebackupbuffer)



def isWorkingFillBlockRandomAddressZero(clsvar):
    if int(CMD_FILLBLOCKRANDOMADDRESSZERO) == int(getEmmcDebugfsAttrValue(clsvar,"cmdindex")) :
        return False
    else:
        return True


'''
Extended CSD rev 1.7 (MMC v5.0)
CID.MANFID = 0x45
[505] Extended Security Commands Error, ext_security_err: 0x00
[504] Supported Command Sets, s_cmd_set: 0x01
[503] HPI features, hpi_features: 0x01
[502] Background operations support, bkops_support: 0x01
[501] Max packed read commands, max_packed_reads: 0x3f
[500] Max packed write commands, max_packed_writes: 0x3f
[499] Data Tag Support, data_tag_support: 0x01
[498] Tag Unit Size, tag_unit_size: 0x03
[497] Tag Resources Size, tag_res_size: 0x03
[496] Context management capabilities, context_capabilities: 0x05
[495] Large Unit size, large_unit_size_m1: 0x00
[494] Extended partitions attribute support, ext_support: 0x03
[493] Supported modes, supported_modes: 0x03
[492] FFU features, FFU_FEATURES: 0x00
[491] Operation codes timeout, operation_code_timeout: 0x10
[490:487] FFU Argument, FFU_ARG: 0x00000000
[305:302] Number of FW sectors correctly programmed, number_of_fw_sectors_correctly_programmed: 0x0
[301:270] Vendor proprietary health report, vendor_proprietary_health_report: 0000000000000000000000000000000000000000000000000000000000000000
[269] Device life time estimation type B, device_life_time_est_typ_b: 0x01
[268] Device life time estimation type A, device_life_time_est_typ_a: 0x01
[267] Pre EOL information, pre_eol_info: 0x01
[266] Optimal read size, optimal_read_size: 0x08
[265] Optimal write size, optimal_write_size: 0x08
[264] Optimal trim unit size, optimal_trim_unit_size: 0x08
[263:262] Device version, device_version: 0x00
[261:254] Firmware version, firmwware_version: 202033302e315343
[253] Power class for 200MHz, DDR at VCC=3.6V, pwr_cl_ddr_200_360: 0xdd
[252:249] Cache size, cache_size 4096 KiB
[248] Generic CMD6 timeout, generic_cmd6_time: 0x19
[247] Power off notification timeout, power_off_long_time: 0x0a
[246] Background operations status, bkops_status: 0x00
[245:242] Number of correctly programmed sectors, correctly_prg_sectors_num 8 KiB
[241] 1st initialization time after partitioning, ini_timeout_ap: 0x50
[239] Power class for 52MHz, DDR at 3.6V, pwr_cl_ddr_52_360: 0x00
[238] POwer class for 52MHz, DDR at 1.95V, pwr_cl_ddr_52_195: 0xdd
[237] Power class for 200MHz, SDR at 3.6V, pwr_cl_200_360: 0xdd
[236] Power class for 200MHz, SDR at 1.95V, pwr_cl_200_195: 0x00
[235] Minimun Write Performance for 8bit at 52MHz in DDR mode, min_perf_ddr_w_8_52: 0x00
[234] Minimun Read Performance for 8bit at 52MHz in DDR modemin_perf_ddr_r_8_52: 0x00
[232] TRIM Multiplier, trim_mult: 0x03
[231] Secure Feature support, sec_feature_support: 0x55
[230] Secure Erase Multiplier, sec_erase_mult: 0xa6
[229] Secure TRIM Multiplier, sec_trim_mult:  0xa6
[228] Boot information, boot_info: 0x07
[226] Boot partition size, boot_size_mult : 0x20
[225] Access size, acc_size: 0x08
[224] High-capacity erase unit size, hc_erase_grp_size: 0x01
[223] High-capacity erase timeout, erase_timeout_mult: 0x03
[222] Reliable write sector count, rel_wr_sec_c: 0x01
[221] High-capacity write protect group size, hc_wp_grp_size: 0x10
[220] Sleep current(VCC), s_c_vcc: 0x08
[219] Sleep current(VCCQ), s_c_vccq: 0x07
[218] Production state awareness timeout, production_state_awareness_timeout: 0x0c
[217] Sleep/awake timeout, s_a_timeout: 0x12
[216] Sleep notification timeout, sleep_notification_time: 0x0d
[215:212] Sector Count, sec_count: 0x03a3e000
[210] Minimum Write Performance for 8bit at 52MHz, min_perf_w_8_52: 0x0a
[209] Minimum Read Performance for 8bit at 52MHz, min_perf_r_8_52: 0x0a
[208] Minimum Write Performance for 8bit at 26MHz, for 4bit at 52MHz, min_perf_w_8_26_4_52: 0x0a
[207] Minimum Read Performance for 8bit at 26MHz, for 4bit at 52MHz, min_perf_r_8_26_4_52: 0x0a
[206] Minimum Write Performance for 4bit at 26MHz, min_perf_w_4_26: 0x0a
[205] Minimum Read Performance for 4bit at 26MHz, min_perf_r_4_26: 0x0a
[203] Power class for 26MHz at 3.6V, pwr_cl_26_360: 0x00
[202] Power class for 52MHz at 3.6V, pwr_cl_52_360: 0x00
[201] Power class for 26MHz at 1.95V, pwr_cl_26_195: 0xdd
[200] Power class for 52MHz at 1.95V, pwr_cl_52_195: 0xdd
[199] Partition switching timing, partition_switch_time: 0x03
[198] Out-of-interrupt busy timing, out_of_interrupt_time: 0x05
[197] IO Driver Strength, driver_strength: 0x01
[196] Device type, device_type: 0x57
[194] CSD structure version, csd_structure: 0x02
[192] Extended CSD revision, ext_csd_rev: 0x07
[191] Command set, cmd_set: 0x00
[189] Command set revision, cmd_set_rev: 0x00
[187] Power class, power_class: 0x0d
[185] High-speed interface timing, hs_timing: 0x01
[181] Erased memory content, erased_mem_cont: 0x00
[179] Partition configuration, partition_config: 0x00
[178] Boot config protection, boot_config_prot: 0x00
[177] Boot bus Conditions, boot_bus_conditions: 0x00
[175] High-density erase group definition, erase_group_def: 0x01
[174] Boot write protection status registers, boot_wp_status: 0x00
[173] Boot area write protection register, boot_wp: 0x00
[171] User area write protection register, user_wp: 0x80
[169] FW configuration, fw_config: 0x00
[168] RPMB Size, rpmb_size_mult: 0x20
[167] Write reliability setting register, wr_rel_set: 0x1f
[166] Write reliability parameter register, wr_rel_param: 0x05
[163] Enable background operations handshake, bkops_en: 0x01
[162] H/W reset function, rst_n_function: 0x00
[161] HPI management, hpi_mgmt: 0x01
[160] Partitioning Support, partitioning_support: 0x07
[159:157] Max Enhanced Area Size, max_enh_size_mult: 0x0006dc
[156] Partitions attribute, partitions_attribute: 0x00
[155] Partitioning Setting, partition_setting_completed: 0x00
[154:152] General Purpose Partition Size, gp_size_mult_4: 0x0
[151:149] General Purpose Partition Size, gp_size_mult_3: 0x0
[148:146] General Purpose Partition Size, gp_size_mult_2: 0x0
[145:143] General Purpose Partition Size, gp_size_mult_1: 0x0
[142:140] Enhanced User Data Area Size, enh_size_mult: 0x0
[139:136] Enhanced User Data Start Address, enh_start_addr: 0x0
[134] Bad Block Management mode, sec_bad_blk_mgmnt: 0x00
[133] Production State Awareness, PRODUCTION_STATE_AWARENESS: 0x00
[131] Periodic Wake-up, periodic_wakeup: 0x00
[130] Program CID CSD in DDR mode support, program_cid_csd_ddr_support: 0x01
[127:64] Vendor Specific Fields, vendor_specific_field[127]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[126]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[125]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[124]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[123]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[122]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[121]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[120]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[119]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[118]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[117]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[116]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[115]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[114]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[113]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[112]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[111]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[110]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[109]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[108]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[107]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[106]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[105]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[104]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[103]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[102]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[101]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[100]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[99]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[98]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[97]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[96]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[95]: 0x02
[127:64] Vendor Specific Fields, vendor_specific_field[94]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[93]: 0x04
[127:64] Vendor Specific Fields, vendor_specific_field[92]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[91]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[90]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[89]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[88]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[87]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[86]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[85]: 0x03
[127:64] Vendor Specific Fields, vendor_specific_field[84]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[83]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[82]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[81]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[80]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[79]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[78]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[77]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[76]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[75]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[74]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[73]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[72]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[71]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[70]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[69]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[68]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[67]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[66]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[65]: 0x00
[127:64] Vendor Specific Fields, vendor_specific_field[64]: 0x00
[63] Native sector size, native_sector_size: 0x00
[62] Sector size emulation, use_native_sector: 0x00
[61] Sector size, data_sector_size: 0x00
[60] 1st initialization after disabling sector size emulation, ini_timeout_emu: 0x0a
[59] Class 6 commands control, class_6_ctrl: 0x00
[58] Number of addressed group to be Released, dyncap_needed: 0x00
[57:56] Exception events control, exception_events_ctrl: 0x08
[55:54] Exception events status, exception_events_status: 0x00
[53:52] Extended Partitions Attribute, ext_partitions_attribute: 0x00
[51:37]Context configuration, context_conf[51]: 0x00
[51:37]Context configuration, context_conf[50]: 0x00
[51:37]Context configuration, context_conf[49]: 0x00
[51:37]Context configuration, context_conf[48]: 0x00
[51:37]Context configuration, context_conf[47]: 0x00
[51:37]Context configuration, context_conf[46]: 0x00
[51:37]Context configuration, context_conf[45]: 0x00
[51:37]Context configuration, context_conf[44]: 0x00
[51:37]Context configuration, context_conf[43]: 0x00
[51:37]Context configuration, context_conf[42]: 0x00
[51:37]Context configuration, context_conf[41]: 0x00
[51:37]Context configuration, context_conf[40]: 0x00
[51:37]Context configuration, context_conf[39]: 0x00
[51:37]Context configuration, context_conf[38]: 0x00
[51:37]Context configuration, context_conf[37]: 0x00
[36] Packed command status, packed_command_status: 0x00
[35] Packed command failure index, packed_failure_index: 0x00
[34] Power Off Notification, power_off_notification: 0x01
[33] Control to turn the Cache On Off, cache_ctrl: 0x01
[30] Mode Config, MODE_CONFIG: 0x00
[26] FFU Status, FFU_STATUS: 0x00
[25:22] Pre loading Data Size, PRE_LOADING_DATA_SIZE: 0x00000000
[21:18] Max Pre Loading Data Size, MAX_PRE_LOADING_DATA_SIZE: 0x00e957f1
[17] Product State Awareness Enablement, PRODUCT_STATE_AWARENESS_ENABLEMENT: 0x02
[16] Secure Removal Type, SECURE_REMOVAL_TYPE: 0x09
'''

def convertHexToStr(strver):
    # strver = "202033302e315343"
    ver =""
    for i in  range(0, len(strver), 2 ):
        ver = chr(int(strver[i:i+2], 16)) + ver
    return ver.strip()



def getEmmcFirmwareVersion(clsvar):
    if hasattr(clsvar, "pathmmc"):
        listlinesext_csd = getEmmcDebugfsAttrValueLines(clsvar,"ext_csd" )
        for lineinfo in listlinesext_csd :
            if "firmwware_version" in lineinfo :
                # return convertHexToStr(lineinfo.split()[-1].strip())
                return lineinfo.split()[-1].strip()
    else:
        print ("No attribute : pathmmc")

def getEmmcLifeValueofext_csd(clsvar):
    if hasattr(clsvar, "pathmmc"):
        listlinesext_csd = getEmmcDebugfsAttrValueLines(clsvar,"ext_csd" )
        for lineinfo in listlinesext_csd :
            if "device_life_time_est_typ_a" in lineinfo :
                return lineinfo.split()[-1].strip()
    else:
        print ("No attribute : pathmmc")

class OnAllStop():
    def __init__(self, clsvar):
        self.clsvar = clsvar
    def set(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnAllStop", 1)
    def clear(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnAllStop", 0)
    def is_set(self):
        if int(getEmmcDebugfsAttrValue(self.clsvar, "OnAllStop")) == 1 :
            return True
        else:
            return False

class OnWaitRestart():
    def __init__(self, clsvar):
        self.clsvar = clsvar
    def set(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnWaitRestart", 1)
    def clear(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnWaitRestart", 0)
    def is_set(self):
        if int(getEmmcDebugfsAttrValue(self.clsvar, "OnWaitRestart")) == 1 :
            return True
        else:
            return False
    def wait(self):
        while(self.is_set() == False) :
            time.sleep(3)

class OnSleepStage():
    def __init__(self, clsvar):
        self.clsvar = clsvar
    def set(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnSleepStage", 1)
    def clear(self):
        setEmmcDebugfsAttrValue(self.clsvar, "OnSleepStage", 0)
    def is_set(self):
        if int(getEmmcDebugfsAttrValue(self.clsvar, "OnSleepStage")) == 1 :
            return True
        else:
            return False
    def wait(self):
        while(self.is_set() == False) :
            time.sleep(3)



'''
capability : 50
erase_size : 4194304
oemid : 0x0100
name : 008GE0
cid : 11010030303847453000912d76b6b000
date : 11/2013
csd : d05e00320f5903ffffffffef92400000
serial : 0x912d76b6
manfid : 0x000011
size : 15269888
'''

dictEmmcDeviceInfo =\
{
    "size"          : "/sys/block/mmcblk0/size",
    "capability"    : "/sys/block/mmcblk0/capability",
    "cid"           : "/sys/block/mmcblk0/device/cid" ,
    "csd"           : "/sys/block/mmcblk0/device/csd" ,
    "date"          : "/sys/block/mmcblk0/device/date" ,
    "erase_size"    : "/sys/block/mmcblk0/device/erase_size" ,
    "manfid"        : "/sys/block/mmcblk0/device/manfid" ,
    # "name"          : "/sys/block/mmcblk0/device/name" ,
    "oemid"         : "/sys/block/mmcblk0/device/oemid" ,
    "serial"        : "/sys/block/mmcblk0/device/serial" ,
}
def gatherEmmcDeviceInfo(clsvar):
    for attr in dictEmmcDeviceInfo :
        if hasattr(clsvar, "adb"):
            clsvar.__dict__[attr] = os.popen("adb shell cat %s"%dictEmmcDeviceInfo[attr]).readline().strip()
        else:
            clsvar.__dict__[attr] = open(dictEmmcDeviceInfo[attr]).readline().strip()

    #print device info
    for attr in dictEmmcDeviceInfo :
        print ("%s : %s " % ( attr, clsvar.__dict__[attr] ))

    clsvar.emmcwholeblocksize = clsvar.size

    ## must call gatherPartitionInfo()
    gatherPartitionInfo(clsvar)

    clsvar.userdata = getpartitioninfo(clsvar, "userdata")


def getManfID(clsvar):

    dictManufacturerid = { 69:"SanDisk", 144:"Hynix", 21:"Samsnung", 17:"Toshiba"}

    if hasattr(clsvar, "adb"):
        manfid = os.popen("adb shell cat /sys/block/mmcblk0/device/manfid").readline().strip()
    else:
        manfid = open("cat /sys/block/mmcblk0/device/manfid").readline().strip()

    fid = int(manfid, 16)

    return dictManufacturerid.get(fid,"No Fid")






''' in case of Sandisk 16G
date : 05/2014
csd : d00f00320f5903ffffffffef8a404000
serial : 0x43aaa4ee
oemid : 0x0100
size : 30777344
cid : 4501005344573136470143aaa4ee5100
erase_size : 524288
capability : 50
manfid : 0x000045
name : SDW16G
{start : 0,     	size : 32768,	size_gap : 0,	crc32 : 2981642449,	checkresult : True,	namepartition : first,	nameblock : first,	}
{start : 32768,	    size : 131072,	size_gap : 0,	crc32 : 1188263875,	checkresult : True,	namepartition : modem,	nameblock : mmcblk0p1,	}
{start : 163840,	size : 2048,	size_gap : 0,	crc32 : 4236209543,	checkresult : True,	namepartition : sbl1,	nameblock : mmcblk0p2,	}
{start : 165888,	size : 1024,	size_gap : 0,	crc32 : 264436575,	checkresult : True,	namepartition : dbi,	nameblock : mmcblk0p3,	}
{start : 166912,	size : 1024,	size_gap : 0,	crc32 : 4058418582,	checkresult : True,	namepartition : DDR,	nameblock : mmcblk0p4,	}
{start : 167936,	size : 4096,	size_gap : 0,	crc32 : 1091212871,	checkresult : True,	namepartition : aboot,	nameblock : mmcblk0p5,	}
{start : 172032,	size : 2048,	size_gap : 0,	crc32 : 561676055,	checkresult : True,	namepartition : rpm,	nameblock : mmcblk0p6,	}
{start : 174080,	size : 2048,	size_gap : 0,	crc32 : 1151580127,	checkresult : True,	namepartition : tz, 	nameblock : mmcblk0p7,	}
{start : 176128,	size : 8,	    size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : pad,	nameblock : mmcblk0p8,	}
{start : 176136,	size : 2048,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : sbl1b,	nameblock : mmcblk0p9,	}
{start : 178184,	size : 1024,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : dbibak,	nameblock : mmcblk0p10,	}
{start : 179208,	size : 2048,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : rpmbak,	nameblock : mmcblk0p11,	}
{start : 181256,	size : 2048,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : tzbak,	nameblock : mmcblk0p12,	}
{start : 183304,	size : 2048,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : rpmf,	nameblock : mmcblk0p13,	}
{start : 185352,	size : 2048,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : tzf,	nameblock : mmcblk0p14,	}
{start : 187400,	size : 1024,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : sdif,	nameblock : mmcblk0p15,	}
{start : 188424,	size : 4096,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : abootf,	nameblock : mmcblk0p16,	}
{start : 192520,	size : 4088,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : spare1,	nameblock : mmcblk0p17,	}
{start : 196608,	size : 32768,	size_gap : 0,	crc32 : 1684505344,	checkresult : True,	namepartition : boot,	nameblock : mmcblk0p18,	}
{start : 229376,	size : 65536,	size_gap : 0,	crc32 : 1802519813,	checkresult : True,	namepartition : persist,	nameblock : mmcblk0p19,	}
{start : 294912,	size : 32768,	size_gap : 0,	crc32 : 661727710,	checkresult : True,	namepartition : recovery,	nameblock : mmcblk0p20,	}
{start : 327680,	size : 6144,	size_gap : 0,	crc32 : 3130896720,	checkresult : True,	namepartition : modemst1,	nameblock : mmcblk0p21,	}
{start : 333824,	size : 6144,	size_gap : 0,	crc32 : 1841929985,	checkresult : True,	namepartition : modemst2,	nameblock : mmcblk0p22,	}
{start : 339968,	size : 8,	    size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : pad1,	nameblock : mmcblk0p23,	}
{start : 339976,	size : 6144,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : fsg,	nameblock : mmcblk0p24,	}
{start : 346120,	size : 1024,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : fsc,	nameblock : mmcblk0p25,	}
{start : 347144,	size : 1024,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : ssd,	nameblock : mmcblk0p26,	}
{start : 348168,	size : 8,	    size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : pad2,	nameblock : mmcblk0p27,	}
{start : 348176,	size : 1024,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : encrypt,	nameblock : mmcblk0p28,	}
{start : 349200,	size : 1024,	size_gap : 0,	crc32 : 1415762891,	checkresult : True,	namepartition : eksst,	nameblock : mmcblk0p29,	}
{start : 350224,	size : 16,	    size_gap : 0,	crc32 : 1824422404,	checkresult : True,	namepartition : rct,	nameblock : mmcblk0p30,	}
{start : 350240,	size : 10208,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : spare2,	nameblock : mmcblk0p31,	}
{start : 360448,	size : 32768,	size_gap : 0,	crc32 : 1615679123,	checkresult : True,	namepartition : misc,	nameblock : mmcblk0p32,	}
{start : 393216,	size : 65536,	size_gap : 0,	crc32 : 67907008,	checkresult : True,	namepartition : laf,	nameblock : mmcblk0p33,	}
{start : 458752,	size : 65536,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : fota,	nameblock : mmcblk0p34,	}
{start : 524288,	size : 32768,	size_gap : 0,	crc32 : 0,	        checkresult : True,	namepartition : spare3,	nameblock : mmcblk0p35,	}
{start : 557056,	size : 16384,	size_gap : 0,	crc32 : 1595974838,	checkresult : False,namepartition : drm,	nameblock : mmcblk0p36,	}
{start : 573440,	size : 16384,	size_gap : 0,	crc32 : 4258071817,	checkresult : True,	namepartition : sns,	nameblock : mmcblk0p37,	}
{start : 589824,	size : 65536,	size_gap : 0,	crc32 : 563020416,	checkresult : False,namepartition : mpt,	nameblock : mmcblk0p38,	}
{start : 655360,	size : 65536,	size_gap : 0,	crc32 : 3871953513,	checkresult : True,	namepartition : factory,nameblock : mmcblk0p39,	}
{start : 720896,	size : 4227072,	size_gap : 0,	crc32 : 3812495658,	checkresult : True,	namepartition : system,	nameblock : mmcblk0p40,	}
{start : 4947968,	size : 1245184,	size_gap : 0,	crc32 : 1385072331,	checkresult : True,	namepartition : cache,	nameblock : mmcblk0p41,	}
{start : 6193152,	size : 524288,	size_gap : 0,	crc32 : 3757066325,	checkresult : True,	namepartition : cust,	nameblock : mmcblk0p42,	}
{start : 6717440,	size : 24018944,size_gap : 0,	                                    namepartition : userdata,nameblock : mmcblk0p43,}
{start : 30736384,	size : 40927,	size_gap : 33,	crc32 : 3715772019,	checkresult : True,	namepartition : grow,	nameblock : mmcblk0p44,	}
'''

BlocksforLGUP = ["sbl1", "rpm", "tz", "aboot", "laf"]

# def cmppartitionstart ( a1, a2 ) :
#     return cmp ( int(a1["start"]), int(a2["start"]) )

def cmppartitionstart3 ( a1 ) :
    return  int(a1["start"])


def gatherPartitionInfo(clsvar):
    # global listv700part
    # listbyname = listv700part.split("\n")
    # print(listbyname)

    if hasattr(clsvar, "listbypartitionname" ) and len(clsvar.listbypartitionname) != 0 :
        listbyname = clsvar.listbypartitionname
    else:
        if hasattr(clsvar, "adb") :
            strdevices = os.popen("adb shell ls /dev/block/platform").readline().strip()
            listbyname = os.popen("adb shell ls -al /dev/block/platform/%s/by-name" % strdevices ).readlines()
        else:
            strdevices = os.popen("ls /dev/block/platform").readline().strip()
            listbyname = os.popen("ls -al /dev/block/platform/%s/by-name" % strdevices ).readlines()

    if len(listbyname) == 0 :
        print("len is 0, use a command 'setenforce 0' ")
        raise Exception("Zero length of listbyname at gatherPartitionInfo")
        exit()

    '''lrwxrwxrwx root     root              1970-01-02 11:56 userdata -> /dev/block/mmcblk0p34 '''
    listdictpartitioninfo = []
    for line in listbyname :
        listtemp = line.split("->")
        if len(listtemp) < 2 :
            continue

        namepartition = listtemp[0].split()[-1].strip()
        nameblock = listtemp[1].split("/")[-1].strip()

        dicttemp = {"start":0, "size":0, "re_size":0, "size_gap":0, "namepartition":"", "nameblock":"", "skipcheck":False, "ret":False, "crc32":0, "checkresult":False }
        dicttemp["namepartition"] = namepartition
        dicttemp["nameblock"] = nameblock
        if hasattr(clsvar, "adb") :
            dicttemp["size"] = os.popen("adb shell cat /sys/block/mmcblk0/%s/size" % nameblock).readline().strip()
            dicttemp["start"] = os.popen("adb shell cat /sys/block/mmcblk0/%s/start" % nameblock).readline().strip()
        else:
            dicttemp["size"] = open("/sys/block/mmcblk0/%s/size" % nameblock).readline().strip()
            dicttemp["start"] = open("/sys/block/mmcblk0/%s/start" % nameblock).readline().strip()
        listdictpartitioninfo.append(dicttemp)

    listdictpartitioninfo.sort(key=cmppartitionstart3)

    print( "listdictpartitioninfo len, %s"%(len(listdictpartitioninfo)))

    ## recalculate the item size due to mis-calculation .
    for i  in range(len(listdictpartitioninfo) -1) :
        currstart = listdictpartitioninfo[i]["start"]
        nextstart = listdictpartitioninfo[i+1]["start"]
        currsize = listdictpartitioninfo[i]["size"]
        listdictpartitioninfo[i]["re_size"] = str( int(nextstart) - int(currstart) )
        listdictpartitioninfo[i]["size_gap"] = str( int(nextstart) - int(currstart) - int(currsize) )

    ## calculate the last partition
    if hasattr(clsvar, "size") :
        listdictpartitioninfo[-1]["re_size"] = str( int(clsvar.emmcwholeblocksize) - int(listdictpartitioninfo[-1]["start"]))
        listdictpartitioninfo[-1]["size_gap"] = str( int(clsvar.emmcwholeblocksize) - int(listdictpartitioninfo[-1]["start"])-int(listdictpartitioninfo[-1]["size"]))
    else:
        print ("@@@@@@@@@@   please  execute gatherEmmcDeviceInfo before gatherPartitionInfo @@@@@@@@@@")
        listdictpartitioninfo[-1]["re_size"] = int(listdictpartitioninfo[-1]["size"])
        listdictpartitioninfo[-1]["size_gap"] = "0"

    ## no first block info ,  create that .
    dicttemp = {"start":0, "size":0, "re_size":0, "size_gap":0, "namepartition":"", "nameblock":"", "skipcheck":False, "ret":False, "crc32":0, "checkresult":False }
    dicttemp["start"] = "0"
    dicttemp["size"] = listdictpartitioninfo[0]["start"]
    dicttemp["re_size"] = listdictpartitioninfo[0]["start"]
    dicttemp["size_gap"] = "0"
    dicttemp["nameblock"] = "first"

    listdictpartitioninfo.insert(0, dicttemp)

    clsvar.partitioninfo =  listdictpartitioninfo


    ## print partition info.
    listpartname = [ "start", "size", "size_gap", "namepartition", "nameblock"]
    for dictparti in listdictpartitioninfo :
        print("{", end="")
        for namepart in listpartname :
            print("%s : %s,"%(namepart, dictparti[namepart]), end="\t")
        print("}", end="\n")



def getpartitioninfo(clsvar, attr):
    if not hasattr(clsvar, "partitioninfo") :
        raise Exception("No partitioninfo")


    for dictparti in clsvar.partitioninfo :
        if attr.lower() == dictparti["namepartition"].lower() :
            return (int(dictparti["start"]), int(dictparti["size"]) )

    raise Exception("No partitioninfo,%s"%(attr))

'''
    how to make the binary file for random number
    makeRandomtxt(1024, "random1024.txt")
    convertToRandomBin("random1024.txt", "random1024.bin")
'''

def fillblockwithzero(clsvar, start, size, countloop ):
    start = int(start)
    size = int(size)

    setEmmcDebugfsAttrValue(clsvar, "addrblockstart", start)
    setEmmcDebugfsAttrValue(clsvar, "countnotsavewrite", size)
    setEmmcDebugfsAttrValue(clsvar, "countloop", countloop)
    setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", CMD_NOTSAVEWRITE)
    # print("%s,%s,%s"%(start, size, countloop))

    if  getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
        return False
    else:
        return True


def fillblocksExceptLGUP(clsvar, msg_client):
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo ")
        return
    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        if  dictparti["namepartition"] in BlocksforLGUP :
            continue
        start = dictparti["start"]
        size = dictparti["re_size"]

        msg_client.SendMsg("fill block with dummy:%s re_size:%s"%(start, size))
        fillblockwithzero(clsvar, start, size, 1 )



def fillRandomwithblockaddress(clsvar, start, loop ):
    # first, check if random address was download into phone .
    if ((not hasattr(clsvar, "sizelistaddrrandom")) or ( clsvar.sizelistaddrrandom != SIZEADDRRANDOM) ) :
        return False

    start = int(start)
    loop = int(loop)

    setEmmcDebugfsAttrValue(clsvar, "addrblockstart", start)
    setEmmcDebugfsAttrValue(clsvar, "countloop", loop)
    setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", "12")

    if  getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
        return False
        print("failed of fillRandomwithblockaddress")
    else:
        return True



def fillblockwithblockaddresszero(clsvar, start, size, fillzero=False ):
    start = int(start)
    size = int(size)

    setEmmcDebugfsAttrValue(clsvar, "addrblockstart", start)
    setEmmcDebugfsAttrValue(clsvar, "countloop", size)
    setEmmcDebugfsAttrValue(clsvar, "retcheck", str(1))
    if fillzero == False :
        setEmmcDebugfsAttrValue(clsvar, "param2", 0)
    else:
        setEmmcDebugfsAttrValue(clsvar, "param2", 100)

    setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", "11")
    result = getEmmcDebugfsAttrValue(clsvar, "result")

    if  result != "0" :
        clsvar.msg_client.SendMsg ("fillblockwithblockaddresszero is failed,%s"% result )
        return False
    else:
        return True


def fillblocksExceptLGUPwithAddress(clsvar, msg_client):
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo ")
        return

    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        if  dictparti["namepartition"] in BlocksforLGUP :
            continue
        start = int(dictparti["start"])
        size = int(dictparti["re_size"])

        msg_client.SendMsg("fill block with address:%s re_size:%s"%(start, size))
        if fillblockwithblockaddresszero(clsvar, start, size) == False :
            msg_client.SendMsg("fill block with address is failed !!!")
            break

def fillblocksSizeGapwithAddress(clsvar, msg_client):
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo ")
        return False

    msg_client.SendMsg("Doing fillblocksSizeGapwithAddress")
    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        if  int(dictparti["size_gap"]) == 0 :
            continue
        start = int(dictparti["start"]) + int(dictparti["size"])
        size = int(dictparti["size_gap"])

        if fillblockwithblockaddresszero(clsvar, start, size) == False :
            msg_client.SendMsg("fill block size_gap with address is failed !!!")
            return  False

    return True

def restoreUserdataWithZero(clsvar, msg_client):
    if not hasattr(clsvar, "listdictcrc") :
        msg_client.SendMsg("No listdictcrc ")
        return False

    listdictcrc = clsvar.listdictcrc
    for dictcrc in listdictcrc :
        start = dictcrc["start"]
        size = dictcrc["size"]
        crc32valuezero = dictcrc["crc32valuezero"]

        if crc32valuezero == True:
            ret = fillblockwithblockaddresszero(clsvar, start, size, True )
            msg_client.SendMsg("fillblockwithblockaddresszero,%s,%s,%s"%(start,size,ret))


def getcrc32ofblocks(clsvar, start, size ):

    msg_client = clsvar.msg_client


    start = int(start)
    size = int(size)

    loop = 1000

    while loop > 0 :

        setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(start))
        setEmmcDebugfsAttrValue(clsvar, "countloop", str(size))
        setEmmcDebugfsAttrValue(clsvar, "retcheck", str(1))
        setEmmcDebugfsAttrValue(clsvar, "cmdeMMCTest", str(13))

        crc32 = getEmmcDebugfsAttrValue(clsvar, "param2")
        result = getEmmcDebugfsAttrValue(clsvar, "result")

        if result == "0" :
            break
        loop -= 1
        msg_client.SendMsg ("crc32blocks left loop,%s"%loop)

    return result, crc32



def getlistbadblocks(clsvar, start, size ):
    start = int(start)
    size = int(size)

    setEmmcDebugfsAttrValue(clsvar, "addrblockstart", str(start))
    setEmmcDebugfsAttrValue(clsvar, "countloop", str(size))
    setEmmcDebugfsAttrValue(clsvar, "retcheck", str(1))
    listtemp = getEmmcDebugfsAttrValueLines(clsvar,"listbadblocks" )
    countbad = getEmmcDebugfsAttrValue(clsvar, "param2")
    if getEmmcDebugfsAttrValue(clsvar, "result") != "0" :
        return False, 0,  []
    else:
        print ("bad block count:%s"%(countbad))
        return True, countbad, listtemp

def getlistbadblocksExceptLGUP(clsvar, msg_client):
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo ")
        return

    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        if  dictparti["namepartition"] in BlocksforLGUP :
            continue
        start = int(dictparti["start"])
        size = int(dictparti["re_size"])

        msg_client.SendMsg("get list bad blocks with address:%s re_size:%s"%(start, size))
        listintblockaddr = getlistbadblocks(clsvar, start, size)
        if len(listintblockaddr)  > 0 :
            str = ",".join(listintblockaddr)
            msg_client.SendMsg("%s:bad block list address:%s " %(dictparti["namepartition"], str))

def skipCheckingBlock(clsvar, msg_client, listblockname ) :
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo in BuildCRC32Table ")
        return False

    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        if  dictparti["namepartition"] in listblockname :
            dictparti["skipcheck"] = True
        else:
            dictparti["skipcheck"] = False

    return True



def BuildCRC32Table(clsvar, msg_client):
    '''
    1. make a mark of crc32 for system area and save in partitioninfo.crc32
    2. fill  block address in userdata
    '''
    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("log,No partitioninfo in BuildCRC32Table ")
        return False

    sec_start = int(round(time.time()))

    crc0filladdress = False
    if hasattr(clsvar, "crc0filladdress") :
        crc0filladdress = clsvar.crc0filladdress


    countSystemSkipCheck = 0
    countSystemRetFail = 0
    countSystemWhole = 0

    # calculate the crc32 for blocks except userdata
    dictpartiUserdata = 0
    msg_client.SendMsg("beginning,BuildCRC32Table")
    listdictpartitioninfo = clsvar.partitioninfo
    for dictparti in listdictpartitioninfo :
        countSystemWhole += 1

        start = dictparti["start"]
        size = dictparti["re_size"]

        if dictparti["skipcheck"] == True or dictparti["namepartition"] == "userdata":
            countSystemSkipCheck += 1
            msg_client.SendMsg("skip,checking,%s,%s,%s,%s"%(start,size,"systemarea", dictparti["namepartition"]))
            if  dictparti["namepartition"] == "userdata" :
                dictpartiUserdata = dictparti
            continue

        ret, crc32 = getcrc32ofblocks(clsvar, start, size )
        dictparti["crc32"] = crc32
        dictparti["ret"] = ret

        if ret != "0" :
            countSystemRetFail += 1
            countSystemSkipCheck += 1
            dictparti["skipcheck"] = True

            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start,size,"systemarea",dictparti["namepartition"],ret ))
        else:
            msg_client.SendMsg("pass,CRC32ed,%s,%s,%s,%s,%s"%(start,size,"systemarea",dictparti["namepartition"],crc32 ) )


    # userdata is big block, split into
    startfill= int(clsvar.userdata[0])

    start = 0
    size = int(clsvar.emmcwholeblocksize)
    inc = int(clsvar.sizetestblock)

    if hasattr(clsvar, "addrcrcstartblock") :
        startfill = int(clsvar.addrcrcstartblock)


    countwholearea = 0
    countwholeareaRetFail = 0
    countwholeareaCRC0Fill = 0

    msg_client.SendMsg("log,start address,%s,size,%s,inc,%s,startfill,%s"%(start, size, inc, startfill))


    listdictcrc  =[]
    pos = 0
    while( size ) :
        countwholearea += 1
        if size < inc :
            inc = size

        ret, crc32 =  getcrc32ofblocks(clsvar, start, inc)
        dicttemp = {"start":start, "size":inc, "ret":ret, "crc32":crc32, "checkresult":False, "skipcheck":False, "crc32valuezero":False}
        if ret != "0":
            countwholeareaRetFail += 1
            # dicttemp["skipcheck"] = True
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,ret ))
        elif ( int(crc32) !=  0 ) :
            msg_client.SendMsg("pass,CRC32ed,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))
        else:
            dicttemp["crc32valuezero"] = True
            if ( crc0filladdress == True ) and (start >= startfill ):
                dicttemp["ret"] = fillblockwithblockaddresszero(clsvar, start, inc)
                if dicttemp["ret"] == True :
                    countwholeareaCRC0Fill += 1
                    ret, crc32 =  getcrc32ofblocks(clsvar, start, inc)
                    if ret != "0" :
                        countwholeareaRetFail += 1
                        # dicttemp["skipcheck"] = True
                        msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,ret ))
                    else:
                        msg_client.SendMsg("pass,Fill & CRC32ed,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))
                    dicttemp["ret"] = ret
                    dicttemp["crc32"] = crc32

                else:
                    countwholeareaRetFail += 1
                    # dicttemp["skipcheck"] = True
                    msg_client.SendMsg("fail,fillblockwithblockaddresszero,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))
            else:
                msg_client.SendMsg("pass,CRC32_0,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))



        listdictcrc.append(dicttemp)
        start += inc
        size -= inc
        pos += 1
    clsvar.listdictcrc = listdictcrc


    msg_client.SendMsg("info,countSystemWhole,%s,countSystemSkipCheck,%s,countSystemRetFail,%s"%(countSystemWhole,countSystemSkipCheck,countSystemRetFail))
    msg_client.SendMsg("info,countwholearea,%s,countwholeareaRetFail,%s,countwholeareaCRC0Fill,%s"%(countwholearea,countwholeareaRetFail,countwholeareaCRC0Fill))

    sec_diff = int(round(time.time())) - sec_start
    msg_client.SendMsg("collapsed_time,%s"%(timedelta(seconds = sec_diff)))

    msg_client.SendMsg("ending,BuildCRC32Table")
    return True


def makeRuntimeBlockAddressNoJournalBlock(clsvar, msg_client):
    '''
    This method should run after BuildCRC32Table.
    And make random address list at runtime.
    But, the addresss list should not include the Journal address which is marked as crc32valuezero == False
    and The size of Block address list is 4K * 1024 = 4M = 8192 blocks
    '''

    SIZEEMMCBLOCK = clsvar.sizetestblock

    listaddress = [kk * 8 for kk in range(SIZEADDRRANDOM)]

    listtemp = listaddress[:SIZEADDRRANDOM]
    clsvar.binlistSequenceAddr = pack("I"*SIZEADDRRANDOM, *listtemp)

    # next time, make the random address .
    random.shuffle(listaddress)
    listtemp = listaddress[:SIZEADDRRANDOM]
    clsvar.binlistRandomAddr = pack("I"*SIZEADDRRANDOM, *listtemp)

    if hasattr(clsvar, "addrstressblock") and clsvar.addrstressblock != 0 :
        return True


    # in case of searching stressblock in userdata
    if not hasattr(clsvar, "userdata") :
        msg_client.SendMsg("No userdata in makeRuntimeBlockAddressNoJournalBlock ")
        return False

    # -----------------------------------------------------------------------------------------
    userdatastart, userdatasize = clsvar.userdata
    msg_client.SendMsg("userdata,start_address,%s,end_address,%s"%(userdatastart, userdatastart+userdatasize))

    # read the crc32 value according to eMMC Block address from a file .
    dicttableaddrcrc32 = {}
    if os.path.exists("crc32.txt") :
        for line in open("crc32.txt") :
            listpairaddrcrc= line.split(",")
            if len(listpairaddrcrc) >= 2 :
                dicttableaddrcrc32[int(listpairaddrcrc[0])] = int(listpairaddrcrc[1])
    else:
        msg_client.SendMsg("No file, crc32.txt")
        return False

    # search the block address of crc32 == 0 ,  > addrblockstart
    listdictcrc = clsvar.listdictcrc
    addrblockstart = userdatastart + int(userdatasize * 2  / 3 )

    if clsvar.EmmcGBSize > 32 :
        addrblockstart = userdatastart + 16384000

    # make addrblockstart 8192 module
    addrblockstart = int(( addrblockstart + ( SIZEEMMCBLOCK - 1 ) ) / (SIZEEMMCBLOCK)) * SIZEEMMCBLOCK

    dictcrcbaseaddr = 0
    dictcrcbaseaddrnext = 0
    boolfindcrc32value_nonzero = False
    boolfindcrc32value_zero = False

    for dictcrc in listdictcrc :
        start = int( dictcrc["start"] )

        if (start < addrblockstart ) :
            continue

        msg_client.SendMsg("start:%s"%start)

        if (boolfindcrc32value_nonzero == False ) :
            if (dicttableaddrcrc32.get(start) == int(dictcrc["crc32"] )) :
                continue
            else:
                boolfindcrc32value_nonzero = True
                continue

        if (boolfindcrc32value_zero == False ) :
            if  dicttableaddrcrc32.get(start) != int(dictcrc["crc32"])  :
                continue
            else:
                dictcrcbaseaddr = dictcrc
                boolfindcrc32value_zero = True
                continue

        if (boolfindcrc32value_zero == True) :
            if ( dicttableaddrcrc32.get(start) == int(dictcrc["crc32"] ) ) :
                continue
            else:
                dictcrcbaseaddrnext = dictcrc
                addrinterval = int( (int(dictcrcbaseaddrnext["start"]) - int(dictcrcbaseaddr["start"])  ) / (SIZEADDRRANDOM * 8 )  )
                if ( addrinterval < 4 ) :
                    # search  again
                    boolfindcrc32value_nonzero = False
                    boolfindcrc32value_zero = False
                    continue

                break


    del dicttableaddrcrc32

    if  (dictcrcbaseaddr == 0 )  or ( int(dictcrcbaseaddr["size"]) < (SIZEADDRRANDOM * 8 ) ) or \
            (dictcrcbaseaddrnext == 0 ) or ( int(dictcrcbaseaddrnext["size"]) < (SIZEADDRRANDOM * 8 )) :
        msg_client.SendMsg("fail,can not identify addrstressblock" )
        return False

    addrinterval = int( (int(dictcrcbaseaddrnext["start"]) - int(dictcrcbaseaddr["start"])  ) / (SIZEADDRRANDOM * 8 )  )
    if ( addrinterval < 4 ) :
        msg_client.SendMsg("addrstressblock,short interval")
        return False

    clsvar.addrstressblock = int(dictcrcbaseaddr["start"]) + int(addrinterval/2) * (SIZEADDRRANDOM * 8 )
    msg_client.SendMsg("addrstressblock,%s"%clsvar.addrstressblock)

    return True




def setupRandomWriteAddr( clsvar, msg_client ):

    if not hasattr(clsvar, "binlistRandomAddr"):
        msg_client.SendMsg ("No binlistRandomAddr")
        return False

    if not hasattr(clsvar, "binlistSequenceAddr"):
        msg_client.SendMsg ("No binlistSequenceAddr")
        return False

    databin = clsvar.binlistRandomAddr
    if clsvar.currEmmcWriteMode == "sequence" : 
        databin = clsvar.binlistSequenceAddr


    try:
        open("%s/listaddrrandom"%(clsvar.pathmmc), 'wb').write(databin)
    except:
        msg_client.SendMsg ("fail,writing random address")
        return False

    # check the size of listaddrrandom
    sizelistaddrrandom = int(getEmmcDebugfsAttrValue(clsvar, "sizelistaddrrandom"))
    if sizelistaddrrandom == SIZEADDRRANDOM :
        clsvar.sizelistaddrrandom = sizelistaddrrandom
        msg_client.SendMsg ("currEmmcWriteMode,%s" % clsvar.currEmmcWriteMode)
        return True
    else:
        msg_client.SendMsg ("fail,setup the random write address ")
        return False

def getPartitionNameOnAddress(clsvar, start, size ):
    start = int(start)
    size = int(size)
    listdictpartitioninfo = clsvar.partitioninfo
    retname = []
    for dictparti in listdictpartitioninfo :
        _start = int(dictparti['start'])
        _size = int(dictparti['size'])

        if _start <= start < _start + _size :
            retname.append(dictparti["namepartition"] )
        elif _start <= start+size < _start + _size :
            retname.append(dictparti["namepartition"] )
        elif start <= _start < start + size :
            retname.append(dictparti["namepartition"] )
        elif start <= _start+_size < start + size :
            retname.append(dictparti["namepartition"] )
        elif start + size < _start :
            break

    return "_".join(retname)

def readAllParition(clsvar, msg_client):

    start = 0
    size = int(clsvar.emmcwholeblocksize)
    inc = int(clsvar.sizetestblock)

    pos = 0
    while( size ) :
        if size < inc :
            inc = size

        ret, crc32 =  getcrc32ofblocks(clsvar, start, inc)

        if ret != "0":
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,ret ))
        else:
            msg_client.SendMsg("pass,CRC32valued,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))

        start += inc
        size -= inc
        pos += 1



def InspectCRC32Table(clsvar, msg_client):

    if clsvar.boolbuildcrc32 == False :
        readAllParition(clsvar, msg_client)
        return

    # if not hasattr(clsvar, "partitioninfo") :
    #     msg_client.SendMsg("log,No partitioninfo in InspectCRC32Table ")
    #     return False

    msg_client.SendMsg("beginning,InspectCRC32Table")

    sec_start = int(round(time.time()))

    countSystemWhole = 0
    countSystemSkipCheck = 0
    countSystemRetFail = 0
    countSystemCRCFail = 0

    listdictpartitioninfo = clsvar.partitioninfo
    dictpartiUserdata = 0
    for dictparti in listdictpartitioninfo :
        countSystemWhole += 1

        start = dictparti["start"]
        size = dictparti["re_size"]

        if dictparti["skipcheck"] == True or dictparti["namepartition"] == "userdata" :
            countSystemSkipCheck += 1
            msg_client.SendMsg("skip,checking,%s,%s,%s,%s"%(start,size,"systemarea", dictparti["namepartition"]))
            if  dictparti["namepartition"] == "userdata" :
                dictpartiUserdata = dictparti
            continue

        ret, crc32 = getcrc32ofblocks(clsvar, start, size )
        if ret != "0" :
            countSystemRetFail += 1
            dictparti["checkresult"] = False
            # dictparti["skipcheck"] = True
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start,size,"systemarea", dictparti["namepartition"], ret))

        else:
            if dictparti["crc32"] == crc32 :
                dictparti["checkresult"] = True
                msg_client.SendMsg("pass,CRC32ed,%s,%s,%s,%s,%s"%(start,size,"systemarea", dictparti["namepartition"],crc32))
            else:
                countSystemCRCFail  += 1
                dictparti["checkresult"] = False
                # dictparti["skipcheck"] = True
                msg_client.SendMsg("fail,CRC32 changed,%s,%s,%s,%s,%s"%(start,size,"systemarea", dictparti["namepartition"],crc32))

        dictparti["ret"] = ret
        dictparti["crc32"] = crc32


    countwholearea = 0
    countwholeareaSkipCheck = 0
    countwholeareaRetFail = 0
    countwholeareaCRCCheckFail = 0


    listdictcrc = clsvar.listdictcrc
    countwholearea = len(listdictcrc)
    msg_client.SendMsg("log,length of wholearea,%s"%(len(listdictcrc)))
    pos = 0
    for dictcrc in listdictcrc :
        start = dictcrc["start"]
        inc = dictcrc["size"]
        ret = dictcrc["ret"]
        crc32 = dictcrc["crc32"]

        if (dictcrc["skipcheck"] == True)  :
            countwholeareaSkipCheck  += 1
            msg_client.SendMsg("skip,checking,%s,%s,%s,%s"%(start, inc,"wholearea",pos ))
            continue

        _ret, _crc32 =  getcrc32ofblocks(clsvar, start, inc)

        if _ret != "0":
            countwholeareaRetFail += 1
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,_ret ))
            dictcrc["checkresult"] = False
            # dictcrc["skipcheck"] = True
        else:
            if int(crc32) != int(_crc32) :
                countwholeareaCRCCheckFail += 1
                msg_client.SendMsg("fail,CRC32 changed,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,_crc32 ))
                dictcrc["checkresult"] = False
                # dictcrc["skipcheck"] = True

            else:
                msg_client.SendMsg("pass,CRC32ed,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos, _crc32 ))
                dictcrc["checkresult"] = True

        dictcrc["ret"] = _ret
        dictcrc["crc32"] = _crc32
        pos += 1

    msg_client.SendMsg("info,countSystemWhole,%s,countSystemSkipCheck,%s,countSystemRetFail,%s,countSystemCRCFail,%s"%(countSystemWhole,countSystemSkipCheck,countSystemRetFail,countSystemCRCFail))
    msg_client.SendMsg("info,countwholearea,%s,countwholeareaSkipCheck,%s,countwholeareaRetFail,%s,countwholeareaCRCCheckFail,%s"%(countwholearea,countwholeareaSkipCheck,countwholeareaRetFail,countwholeareaCRCCheckFail))

    sec_diff = int(round(time.time())) - sec_start
    msg_client.SendMsg("collapsed_time,%s"%(timedelta(seconds = sec_diff)))

    msg_client.SendMsg("ending,InspectCRC32Table")
    return True

def printpartitioninfo(clsvar, msg_client):

    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo in InspectCRC32Table ")
        return False

    msg_client.SendMsg("______ printpartitioninfo _____ ")
    listdictpartitioninfo = clsvar.partitioninfo

    for dictparti in listdictpartitioninfo :
        ## str(dictpartiUserdata)
        ## "{'checkresult': False, 'size_gap': 0, 'start': 0, 'skipcheck': False, 'nameblock': '', 'namepartition': '', 'size': 0, 're_size': 0, 'ret': False, 'crc32': 0}"
        strinfo = "start,%s,size,%s,ret,%s,skipcheck,%s,checkresult,%s,CRC32,%s,nameblock,%s,namepartition,%s,size_gap,%s,re_size,%s"% ( \
            dictparti["start"],dictparti["size"],dictparti["ret"],dictparti["skipcheck"],dictparti["checkresult"],dictparti["crc32"],\
            dictparti["nameblock"],dictparti["namepartition"],dictparti["size_gap"],dictparti["re_size"] )
        msg_client.SendMsg(strinfo)

    msg_client.SendMsg("----------- userdata partition result ---------------")

    ##{"start":start, "size":inc, "ret":ret, "crc32":crc32, "checkresult":False, "skipcheck":False, "crc32valuezero":False}

    listdictcrc = clsvar.listdictcrc
    for dictcrc in listdictcrc :
        strinfo = "start,%s,size,%s,ret,%s,skipcheck,%s,checkresult,%s,CRC32,%s,crc32valuezero,%s"% ( \
            dictcrc["start"],dictcrc["size"],dictcrc["ret"],dictcrc["skipcheck"],dictcrc["checkresult"],dictcrc["crc32"],dictcrc["crc32valuezero"] )
        msg_client.SendMsg(strinfo)

    msg_client.SendMsg("______ finish: printpartitioninfo _____ ")
    return True



def printEmmcBlockinfo(clsvar, msg_client) :
    start = 0
    size = int(clsvar.emmcwholeblocksize)
    inc = int(clsvar.sizetestblock)

    pos = 0
    while( size ) :
        if size < inc :
            inc = size

        ret, crc32 =  getcrc32ofblocks(clsvar, start, inc)
        if ret == "0" :
            msg_client.SendMsg("pass,CRC32ed,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,crc32 ))
        else:
            msg_client.SendMsg("fail,CRC32 not,%s,%s,%s,%s,%s"%(start, inc,"wholearea",pos,ret ))

        start += inc
        size -= inc
        pos += 1