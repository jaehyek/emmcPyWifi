# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""


def main():
    pass

import os

def printout ( f, msg ) :
    if f != None:
        f.write(msg)
    print ( msg, end="")



if __name__ == "__main__":

    import argparse
    fileincsv = ""

    cmdlineopt = argparse.ArgumentParser(description='filter the interest csv field from csv file ')
    cmdlineopt.add_argument('-o', action="store", dest="fileout", default='fileout.csv', help='output csv file .')
    cmdlineopt.add_argument('-dir', action="store", dest="dir", default='.', help='working dir .')
    # cmdlineopt.add_argument('pos1')

    cmdlineresults = cmdlineopt.parse_args()

    # print (cmdlineresults.pos1 )
    # print (cmdlineresults.fileout )
    f = None
    if cmdlineresults.fileout :
        f = open(cmdlineresults.fileout, "w")

    listcsv = []
    if cmdlineresults.dir :
        listcsv = os.listdir(cmdlineresults.dir)
    else:
        listcsv = os.listdir(".")

    listdict = []

    for filename in listcsv :
        filebase, ext = os.path.splitext(filename)
        if ext.lower() != ".csv" :
            continue
        dicttemp = {}
        dicttemp["id"] = filebase

        finddead = False
        for line in open(os.path.join(cmdlineresults.dir, filename), "r") :
            listitems = line.strip().split(",")
            while(len(listitems) != 8 ):
                listitems.append("")
            mtime, id, model, func, item1, val1, item2, val2 =tuple(listitems)

            if "@" in item1 :
                continue

            if "currcountLDO20shaking" in item1 :
                dicttemp["currcountLDO20shaking"] = val1
                dicttemp["currEmmcVDD"] = val2
            elif "currmtimeSleepdown" in item1 :
                dicttemp["currmtimeSleepdown"] = val1
            elif "currmtimeSleepup" in item1 :
                dicttemp["currmtimeSleepup"] = val1
            elif "addruserblockstart" in item1 :
                dicttemp["addruserblockstart"] = val1
            elif "EmmcFirmwareVersion" in item1 :
                dicttemp["EmmcFirmwareVersion"] = val1
            elif "emmcLifeValue" in item1 :
                if int(val1) <= 11 :
                    dicttemp["emmcLifeValue"] = val1
                else:
                    finddead = True
                    break
        if finddead == False:
            dicttemp["emmcLifeValue"] = "still loop"

        listdict.append(dicttemp)

    # print("print out result")
    listhead = ["id","addruserblockstart", "EmmcFirmwareVersion", "emmcLifeValue", "currEmmcVDD","currmtimeSleepup", "currmtimeSleepdown", "currcountLDO20shaking"  ]

    strhead = ",".join(listhead)
    printout (f, strhead + "\n")
    for dicttemp in listdict :
        for itemname in listhead :
            itemvalue = dicttemp[itemname] + ","
            printout (f, itemvalue)
        printout(f,"\n")

    if f :
        f.close()






    # if len(cmdlineresults.fileincsv) == 0 :
    #    print " Must have the value of fileincsv as parameter"
    #    exit()
    #
    # fileincsv = cmdlineresults.fileincsv
    #

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