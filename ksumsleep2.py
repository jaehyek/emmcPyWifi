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

    
def sumDOE(clsvar,filename):

    fout = open(clsvar.fileout_doe, 'a')
    fin = open(filename, "r")

    for line in fin :
        listitem = line.split(",")
        if listitem[1] == "diffref" and listitem[0] == "InspectCRC32Table" :
            fout.write(filename + ",")
            fout.write(line)

    fin.close()
    fout.close()




def updatefilenames(clsvar) :
    clsvar.filenames = []
    for root, dirs, files in os.walk("."):
        # deal files only with root == "."
        if root == "." :
            for filename in files :
                if filename[-8:-4] == "_out" and (not "ref" in filename ):
                    clsvar.filenames.append(filename)



if __name__ == "__main__":
    cmdlineopt = argparse.ArgumentParser( description='extract the DOE data from file_out.csv, and print to filename file_doe.csv')
    cmdlineopt.add_argument('-dir', action="store", dest="dir",  default='.', help='working directory')
    cmdlineopt.add_argument('-a', action="store_true", dest="allfile",  default=False, help='process all files matching  *_out.csv')
    cmdlineopt.add_argument('-out', action="store", dest="fileout_doe",  default=False, help='DOE data file name for output')

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

    for filename in clsvar.filenames :
        sumDOE(clsvar, filename)
        print("doeing.... %s"%filename)
