# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""

import argparse
import os
from collections import OrderedDict

def makeDictDictCountToOrderedList(dictdictcount):
    dictcount = {}
    for itemkey in dictdictcount :
        dicttemp = dictdictcount.get(itemkey)
        dictcount[itemkey] = dicttemp["count"]

    odictfailcount = OrderedDict(sorted(dictcount.items(), key=lambda t: t[0]))

    strret = []
    for itemkey in odictfailcount :
        count = odictfailcount.get(itemkey)
        strret += [itemkey, str(count)]

    return strret

def getdiffreason(listref, listreason ) :

    lenlist = len(listreason)
    listcheck = [ "CRC32 not", "CRC32 changed"]

    countCRC32not = 0
    countCRC32Changed = 0
    for index in range(lenlist):
        if listreason[index] == "CRC32 not"  and listref[index] != "fail" :
            countCRC32not += 1
        elif listreason[index] == "CRC32 changed"  and listref[index] != "fail" :
            countCRC32Changed += 1

    return ["countCRC32not", str(countCRC32not), "countCRC32Changed", str(countCRC32Changed)]


def getdiffref(listref, listsum) :

    lenlist = len(listsum)
    countfail = 0
    for index in range(lenlist):
        if listsum[index] == "fail"  and listref[index] != "fail" :
            countfail += 1
    return countfail

    
def csvsum(clsvar,filename):
    print("csvfile,%s"%(filename), end=",")
    fileext = os.path.splitext(filename)
    fileout = fileext[0] + "_out" + fileext[1]

    fout = open(fileout, 'w')
    fin = open(filename, "r")

    

    # aa0             ,aa1        ,aa2               ,aa3    ,aa4            ,aa5 ,aa6    ,aa7   ,aa8  ,aa9 ,aa10      ,aa11
    # 2015-03-27 17:57,1.42745E+12,LGD8551516c032_ref,LG-D855,BuildCRC32Table,pass,CRC32ed,165888,1024 ,dbi ,CRC32     ,2962355554
    # 2015-03-27 17:59,1.42745E+12,LGD8551516c032_ref,LG-D855,BuildCRC32Table,pass,CRC32ed,524288,65536,TRUE,1823115069
    # 2015-03-27 17:57,1.42745E+12,LGD8551516c032_ref,LG-D855,<module>       ,EmmcGBSize : 29

    prevstage = ""
    listcheckstage = [ "BuildCRC32Table", "InspectCRC32Table"]
    listjudge = [ "pass", "fail", "skip" ]
    EmmcGBSize = 0
    EmmcBulksize = 0
    EmmcBulkcount = 0
    countdeepsleep = 0
    countdeepsleepstage = 0

    countdeepsleepprev = 0

    countnodeepsleep = 0
    countnodeepsleepstage = 0

    # 0 : No_Deep_Sleep, 1:number for previous sleep count
    typecountdeepsleepprev = 1
    listpassfail = []
    listaccumulate = []
    listref = []
    dictoutstage = {}
    EmmcFirmwareVersion = ""
    boolref = False
    listcurrset = []
    listadditionalfail = []
    countCRC32Not = 0



    for line in fin :
        listitem = line.strip().split(",")
        lenlist = len(listitem)

        if lenlist <= 5 :
            continue

        currentstage = listitem[4]
        strtag = listitem[5]


        #----- inside of checking stage  -------------
        if  currentstage in listcheckstage :
            # print (line)
            if EmmcGBSize == 0 :
                print("EmmcGBSize not defined")
                return False



            # at the end of stage, summerize the fail/pass lsit of listpassfail
            if strtag == "ending"  :
                countdeepsleep += countdeepsleepstage
                countnodeepsleep +=  countnodeepsleepstage
                #print diff between listref and listpassfail
                if boolref == True :
                    listcountdiff = getdiffreason(listref, listpassfail)
                    fout.write(",".join([currentstage] + ["diffref"]+ [str(EmmcFirmwareVersion),str(EmmcGBSize)]+ listcurrset + listcountdiff + [str(countdeepsleepstage)] +  listadditionalfail ) + "\n")

                fout.write(",".join([currentstage] + listpassfail) + "\n")

                listpassfail = []
                prevstage = ""
                listcurrset = []
                listadditionalfail = []
                countdeepsleepstage = 0
                countnodeepsleepstage = 0
                continue

            # new stage
            if currentstage != prevstage and len(listpassfail) == 0 :
                prevstage = currentstage
                listpassfail = ["n"] * EmmcBulkcount

            if lenlist < 9 :
                continue

            strreason = listitem[6]
            straddr = listitem[7]
            strinc = listitem[8]
            strarea = listitem[9]
            strpos = listitem[10]

            # record the fail reason in listpassfail and listaccumulate .
            # if strtag in listjudge and straddr.isdigit() :
            #     idx, mod = divmod(int(straddr), EmmcBulksize)
            #     if mod != 0 :
            #         continue

            if strtag in listjudge and strarea == "wholearea" :
                idx = int(strpos.strip())

                if strtag == "fail" :
                    listpassfail[idx] = strreason
                    if strreason.lower() =="CRC32 changed".lower() :
                        listaccumulate[idx] = strtag
                    elif strreason.lower() == "CRC32 not".lower() :
                        countCRC32Not += 1
                else:
                    listpassfail[idx] = strtag

                continue

        #----- outside of checking stage  -------------
        elif currentstage == "scenario_sleepwake" :
            listitem[-1] = listitem[-1].strip()
            if strtag == "fail" :
                listadditionalfail += listitem[6:]
                # listitem[6] == reason
                dictoutstage.setdefault(listitem[6], {"count":0} )['count'] += 1
                continue
            elif strtag == "curr set" :
                listcurrset += listitem[5:]
                continue
            elif strtag == "No_Deep_Sleep" :
                typecountdeepsleepprev = 0
                countnodeepsleepstage += 1
                continue
            elif strtag == "countdeepsleep" and listitem[6].strip().isdigit() == True :
                countdeepsleepcurr = int(listitem[6].strip())

                if typecountdeepsleepprev == 1 :
                    countdeepsleepstage += 1
                elif typecountdeepsleepprev == 0  and countdeepsleepcurr != countdeepsleepprev :
                    if countdeepsleepprev == 0 :
                        countdeepsleepstage += 1
                    else :
                        countdeepsleepstage += countdeepsleepcurr - countdeepsleepprev

                countdeepsleepprev = countdeepsleepcurr
                typecountdeepsleepprev = 1
                continue




        #----- find the bulksize  ----------------
        elif "main" in  currentstage and "clsvar.sizetestblock" in listitem[5] and EmmcBulksize == 0 :
            EmmcBulksize = int(listitem[6].strip())
            print("EmmcBulksize,%s"%EmmcBulksize, end=",")
            continue

        #----- find the EmmcGBSize  ----------------
        elif "main" in  currentstage and "EmmcGBSize" in listitem[5] and EmmcGBSize == 0 :
            listtemp = listitem[5].split(":")
            if len(listtemp) >= 2 :
                EmmcGBSize = int(listtemp[1])
            else:
                EmmcGBSize = int(listitem[6])

            EmmcGBSize = int((EmmcGBSize + 3.9 ) / 4) * 4

            print("EmmcGBSize,%s"%EmmcGBSize, end=",")
            continue

        #----- check the parameter, and prepare the EmmcBulkcount, listaccumulate ----------------
        elif "pretask" in  currentstage  and EmmcBulkcount == 0  :
            if EmmcGBSize == 0 or EmmcBulksize == 0 :
                print("No data of EmmcGBSize or  EmmcBulksize \n")
                exit()

            EmmcBulkcount = int(EmmcGBSize * 1024 * 2 * 1024 / EmmcBulksize)
            
            # write the csv head line
            headline = []
            for idx in range(EmmcBulkcount) :
                headline.append("aa%s"%idx)
            headline = ",".join(["stage"] + headline) + "\n"
            fout.write(headline)
            del headline

            # write listref to fout if clsvar.listref exist .
            if hasattr(clsvar, "listref") :
                listref = clsvar.listref
                fout.write(",".join(["ref"] + listref) + "\n")
                boolref = True ;

            listaccumulate = ['n'] * EmmcBulkcount
            continue

        #----- find the EmmcFirmwareVersion  ----------------
        elif "main" in  currentstage and "EmmcFirmwareVersion" in listitem[5] and len(EmmcFirmwareVersion) == 0  :
            EmmcFirmwareVersion = listitem[6].strip()
            print("EmmcFirmwareVersion,%s"%EmmcFirmwareVersion, end=",")
            continue



    # file write with summary info
    if clsvar.sum == True :
        fsum = open(fileext[0] + "_sum.csv", "w")
        strsum = ",".join( ["summary"] + listaccumulate)
        fsum.write(strsum)
        fsum.close()

    # print the fail count of listaccumulate
    if boolref == True :
        print("faildiffcount,%s"%(getdiffref(listref, listaccumulate)), end="," )

    else:
        countfail = 0
        for result in listaccumulate :
            if result == "fail" :
                countfail += 1
        print("failsumcount,%s"%(countfail), end="," )

    print("deepsleep count,%s"%countdeepsleep, end=",")
    print("NoDeepSleep count,%s"%countnodeepsleep, end=",")
    print("CRC32 Not count,%s"%(countCRC32Not), end=",")

    # print the fail count of outside stage .
    print(",".join(makeDictDictCountToOrderedList(dictoutstage)), end="," )


    print("", end="\n")

    if filename[-8:-4] == "_ref" :
        clsvar.listref = listaccumulate

    fin.close()
    fout.close()




def updatefilenames(clsvar) :
    clsvar.filenames = []
    for root, dirs, files in os.walk("."):
        # deal files only with root == "."
        if root == "." :
            for filename in files :
                if filename[-4:] != ".csv" :
                    continue
                if filename[-8:-4] == "_out" :
                    continue
                if filename[-8:-4] == "_sum" :
                    continue
                if "doe" in filename or "DOE" in filename :
                    continue
                if filename[-8:-4] == "_ref" :
                    clsvar.ref = filename
                    continue
                clsvar.filenames.append(filename)



if __name__ == "__main__":
    cmdlineopt = argparse.ArgumentParser( description='extract the emmc test result from cvs files, and print summary to file_out.csv and file_sum.csv')
    cmdlineopt.add_argument('-dir', action="store", dest="dir",  default='.', help='working directory')
    cmdlineopt.add_argument('-a', action="store_true", dest="allfile",  default=False, help='process all files')
    cmdlineopt.add_argument('-sum', action="store_true", dest="sum",  default=False, help='summary to sum file')
    cmdlineopt.add_argument('-ref', action="store", dest="ref",  help='summary csv file to refer for 32G')
    cmdlineopt.add_argument(dest='filenames', metavar='filename', nargs='*')

    clsvar = cmdlineopt.parse_args()

    try:
        os.chdir(clsvar.dir)
        print(os.path.abspath(os.curdir))
    except:
        print("can't change to the working directory")
        exit()

    if clsvar.allfile == True :
        updatefilenames(clsvar)

    if len(clsvar.filenames) == 0 :
       print ("error : No filename")
       exit()

    print (clsvar.filenames)

    if clsvar.ref != None and len(clsvar.ref) > 0 :
        csvsum(clsvar, clsvar.ref)

    for filename in clsvar.filenames :
        csvsum(clsvar, filename)
