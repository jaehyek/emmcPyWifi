# -*- coding: utf-8 -*-
import argparse
import os

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""


def getcrc32not(clsvar):
    counttotal = 0
    for csv in clsvar.listcsv :

        dicttemp = {}
        for line in  open(csv, "r") :
            listitem = line.split(",")
            if len(listitem) > 7 and listitem[6] == "CRC32 not" :
                dicttemp.setdefault(listitem[10], {"count":0, "item":line })["count"] += 1

        countlocal = len(dicttemp)
        counttotal += countlocal
        print("----,filename,%s,count,%s"%(csv,countlocal))
        if countlocal > 0 :
            for key in dicttemp :
                print ( dicttemp[key]["item"].strip() + "," + str(dicttemp[key]["count"]))

    print("----,counttotal,%s"%counttotal)



def updatefilenames(clsvar) :
    clsvar.listcsv = []
    for root, dirs, files in os.walk("."):
        # deal files only with root == "."
        if root == "." :
            for filename in files :
                if filename[-4:] == ".csv" :
                    clsvar.listcsv.append(filename)


if __name__ == "__main__":

    cmdlineopt = argparse.ArgumentParser( description='gather the CRC32 not from csv file ')
    cmdlineopt.add_argument('-dir', action="store", dest="dir",  default='.', help='working directory')
    cmdlineopt.add_argument('-out', action="store", dest="fileout", default='crc32not.list', help='file name to write')
    cmdlineopt.add_argument(dest='listcsv', metavar='coordinate', nargs='*')

    clsvar = cmdlineopt.parse_args()

    os.chdir(clsvar.dir)
    print(os.path.abspath(os.curdir))

    if len(clsvar.listcsv)  == 0 :
        updatefilenames(clsvar)

    getcrc32not(clsvar)




