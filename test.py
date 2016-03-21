# -*- coding: utf-8 -*-
import os

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""

from emmcconfig import getModelInfo
import emmcfunc
import os

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



def maketestblock(clsvar, msg_client):
    '''
    This method should run after BuildCRC32Table.
    And make random address list at runtime.
    But, the addresss list should not include the Journal address which is marked as crc32valuezero == False
    and The size of Block address list is 4K * 1024 = 4M = 8192 blocks
    '''


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
    addrblockstart = int(( addrblockstart + ( 8192 - 1 ) ) / (8192)) * 8192

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
                addrinterval = int( (int(dictcrcbaseaddrnext["start"]) - int(dictcrcbaseaddr["start"])  ) / (emmcfunc.SIZEADDRRANDOM * 8 )  )
                if ( addrinterval < 4 ) :
                    # search  again
                    boolfindcrc32value_nonzero = False
                    boolfindcrc32value_zero = False
                    continue
                break


    del dicttableaddrcrc32

    if  (dictcrcbaseaddr == 0 )  or ( int(dictcrcbaseaddr["size"]) < (emmcfunc.SIZEADDRRANDOM * 8 ) ) or \
            (dictcrcbaseaddrnext == 0 ) or ( int(dictcrcbaseaddrnext["size"]) < (emmcfunc.SIZEADDRRANDOM * 8 )) :
        msg_client.SendMsg("fail,can not identify addrstressblock" )
        return False

    addrinterval = int( (int(dictcrcbaseaddrnext["start"]) - int(dictcrcbaseaddr["start"])  ) / ( emmcfunc.SIZEADDRRANDOM * 8 )  )
    if ( addrinterval < 4 ) :
        msg_client.SendMsg("addrstressblock,short interval")
        return False

    clsvar.addrstressblock = int(dictcrcbaseaddr["start"]) + int(addrinterval/2) * (emmcfunc.SIZEADDRRANDOM * 8 )
    msg_client.SendMsg("addrstressblock,%s"%clsvar.addrstressblock)

    return True



def readbuildinfo (clsvar,  csvfile ) :
    listdictcrc = []
    for line in open(csvfile) :
        line = line.strip()
        listitem = line.split(",")
        dicttemp = { "start": listitem[0], "crc32":listitem[1], "size":8192}
        listdictcrc.append(dicttemp)

    clsvar.listdictcrc = listdictcrc


clsvar = emmcfunc.clsVariables()
getModelInfo(clsvar)

emmcfunc.gatherPartitionInfo(clsvar)
msg_client = clsMsgClent( "%s_%s_%s"%("Asd" ,"asdf", "asd") ,"test","server", 20000 )
msg_client.onlylocal = True

readbuildinfo(clsvar, "bb.csv")

clsvar.userdata = ( 6946816, 23822336 )
clsvar.EmmcGBSize = 16

maketestblock(clsvar, msg_client)