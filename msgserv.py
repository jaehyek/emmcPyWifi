#!/usr/bin/env python3
from __future__ import print_function
import sys
if sys.version[0] == "2" :
    from SocketServer import StreamRequestHandler, TCPServer
else:
    from socketserver import StreamRequestHandler, TCPServer

import socket
# import multiprocessing
import threading
import time
from datetime import datetime, timedelta
from emmcconfig import getModelInfo

def ConvertTimeStampToString ( timestampmilisecond ):
    if timestampmilisecond == None:
        return ""
    strfmt = "%Y-%m-%d %H:%M:%S"
    outdatetime = datetime(1970, 1, 1) + timedelta(hours= 9, milliseconds=timestampmilisecond)
    return outdatetime.strftime(strfmt)

def ConvertDateTimeToMiliSeconds( y, m, d, h = 0 , minute = 0 , s = 0 ):
    daydiff = datetime(y, m, d, h, minute, s) - datetime(1970, 1, 1, 9, 0, 0)
    return int(daydiff.total_seconds()) * 1000
'''
print ConvertTimeStampToString(1340751010888)
print ConvertDateTimeToMiliSeconds(2012, 6, 26, 22, 50, 10)
exit()
--> result---
2012-06-26 22:50:10
1340751010000

'''

class CLSVAR():
    def __init__(self):
        pass

class EchoHandler(StreamRequestHandler):
    timeout = 5*60
    rbufsize = -1
    wbufsize = 0
    disable_nagle_algorithm = False
    def handle(self):
        print('Got connection from', self.client_address)
        # self.rfile is a file-like object for reading

        f = 0
        try:
            for line in self.rfile:
                # self.wfile is a file-like object for writing
                # send repsonse
                self.wfile.write("1".encode())

                ID = line.decode().split(",")[0].strip()
                filename = ID + ".csv"
                f = open(filename, 'a')
                timenow = int(round(time.time() * 1000))
                lineadd = ConvertTimeStampToString(timenow) + "," + str(timenow)+ "," +  line.decode()

                f.write(lineadd)
                print (line)
        except socket.timeout :
            self.rfile.close()
            self.wfile.close()
            print('Timed out!')

        if f :
            f.close()
            print ("closing file.")


if __name__ == '__main__':
    clsvar = CLSVAR()
    getModelInfo(clsvar)
    NWORKERS = 300
    serv = TCPServer(('', clsvar.port), EchoHandler)
    for n in range(NWORKERS):
        # t = multiprocessing.Process( target=serv.serve_forever)
        t = threading.Thread( target=serv.serve_forever)
        t.daemon = True
        t.start()
        print ("creating new TCP thread %s" % n )
    print('Multithreaded server running on port 20000')
    serv.serve_forever()
