# -*- coding: utf-8 -*-
from __future__ import print_function


__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""

import os
import pickle


def printpartitioninfo(clsvar, msg_client):

    if not hasattr(clsvar, "partitioninfo") :
        msg_client.SendMsg("No partitioninfo in InspectCRC32Table ")
        return False

    msg_client.SendMsg("______ printpartitioninfo _____ ")
    listdictpartitioninfo = clsvar.partitioninfo
    dictpartiUserdata = 0
    for dictparti in listdictpartitioninfo :
        if  dictparti["namepartition"] == "userdata" :
            dictpartiUserdata = dictparti
            continue

        ## str(dictpartiUserdata)
        ## "{'checkresult': False, 'size_gap': 0, 'start': 0, 'skipcheck': False, 'nameblock': '', 'namepartition': '', 'size': 0, 're_size': 0, 'ret': False, 'crc32': 0}"
        strinfo = "start,%s,size,%s,ret,%s,skipcheck,%s,checkresult,%s,CRC32,%s,nameblock,%s,namepartition,%s,size_gap,%s,re_size,%s"% ( \
            dictparti["start"],dictparti["size"],dictparti["ret"],dictparti["skipcheck"],dictparti["checkresult"],dictparti["crc32"],\
            dictparti["nameblock"],dictparti["namepartition"],dictparti["size_gap"],dictparti["re_size"] )
        msg_client.SendMsg(strinfo)

    msg_client.SendMsg("----------- userdata partition result ---------------")

    ##{"start":start, "size":inc, "ret":ret, "crc32":crc32, "checkresult":False, "skipcheck":False, "crc32valuezero":False}
    if ((clsvar.setupMarkforUserdata == "addrfillfull") or (clsvar.setupMarkforUserdata == "addrfillpartial") )  :
        msg_client.SendMsg("mark type : addrfillfull or addrfillpartial ")
    else:
        ## clsvar.setupMarkforUserdata == crc32 ;
        listdictcrc = clsvar.listdictcrc
        for dictcrc in listdictcrc :
            strinfo = "start,%s,size,%s,ret,%s,skipcheck,%s,checkresult,%s,CRC32,%s,crc32valuezero,%s"% ( \
                dictcrc["start"],dictcrc["size"],dictcrc["ret"],dictcrc["skipcheck"],dictcrc["checkresult"],dictcrc["crc32"],dictcrc["crc32valuezero"] )
            msg_client.SendMsg(strinfo)

    msg_client.SendMsg("______ finish: printpartitioninfo _____ ")
    return True



class MSG_CLIENT() :
    def __init__(self):
        pass
    def SendMsg(self, msg) :
        print(msg)

if __name__ == "__main__":

    ## ______________ initialize the variables class   __________________
    if os.path.exists("clsvar.pickle") :
        with open('clsvar.pickle', 'rb') as handle:
            clsvar = pickle.load(handle)
    else :
        print("No clsvar.pickle")
        exit()

    msg_client = MSG_CLIENT()
    printpartitioninfo(clsvar, msg_client)

