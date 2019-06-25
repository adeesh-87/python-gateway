from __future__ import print_function
from threading import Thread
from threading import Timer
import Queue as Queue
import random
import serial
import time
import struct
#import timeit
import csv

byteQueue = Queue.Queue(maxsize=1000)
packetQueue = Queue.Queue(maxsize=200)

readerRunning = 1

MAGIC_BYTE = bytearray.fromhex('10')
SOF_BYTE = bytearray.fromhex('02')
EOF_BYTE = bytearray.fromhex('03')

states = {
    '__IDLE',
    '__MAGIC',
    '__SOF',
    '__DATA_RX',
    '__FCS_RX',
    '__ERROR'
}

parserState = '__IDLE'

coordCmds = ['16', '72', '71', '73', '74', '75']

coordInitStream = bytearray.fromhex("10 02 16 00 00 00 00 00 00 00 00 02 02 00 00 10 03 3F")
tt = time.time()

def parser():
    global readerRunning
    global parserState
    numPackets = 0
    while readerRunning == 1: 
        time.sleep(.2)
        chkSum = 0
        packet = []
        while byteQueue.qsize():
            bb = byteQueue.get()
            #chkSum = chkSum + int(bb.encode('hex'),16)
            #print(bb.encode('hex'),":",end='')
            if (parserState == '__IDLE') and (bb == MAGIC_BYTE):
                parserState = '__SOF'
                #print("sof")
                #continue
            elif (parserState == '__SOF') and (bb == SOF_BYTE):
                parserState = '__DATA_RX'
                #continue
                #print("data")
            elif (parserState == '__DATA_RX'):
                if bb == MAGIC_BYTE:
                    parserState = '__MAGIC'
                    #print("mag")
                    #chkSum = chkSum + int(bb.encode('hex'),16)
                else :
                    chkSum = chkSum + int(bb.encode('hex'),16)
                    packet.append(bb)
                    #print("yo")
                    #print("check sum: ", hex(chkSum))
                    #gg = gg + format(bb, 'x').zfill(2) + ","
                #continue
            elif (parserState == '__MAGIC'):
                if bb == EOF_BYTE:
                    parserState = '__FCS_RX'
                    #print("fcs")
                else :
                    chkSum = chkSum + int(bb.encode('hex'),16)
                    chkSum = chkSum + int(bb.encode('hex'),16)
                    packet.append(bb.encode('hex'))
                    #print("yo10")
                    #chkSum = chkSum + bb
                    #gg = gg + format(bb, 'x').zfill(2) + ","
                    parserState = '__DATA_RX'
                #continue
            elif (parserState == '__FCS_RX'):
                if int(bb.encode('hex'),16) == ((chkSum + 0x25))%0x100:
                    
                    packetQueue.put(packet)
                    numPackets = numPackets + 1
                    print(" [*] Pkt RX: ", unpack('>B',packet)
                    packet=[]
                    chkSum = 0
                    parserState = '__IDLE'

                else:
                    print(" [*] Checksum Mismatch: ", hex((chkSum+0x25)%0x100))
                    packet = []
                    chkSum = 0
                    parserState = '__IDLE'
                #continue
            
            
        #print()
        #print("check sum: ", hex(chkSum%0x100))
        #time.sleep(1) # This is erroneous, during sleep some bytes may come to queue


def reader():
    #linkSafetyTimerFired1 = 0
    #linkSafetyTimerFired2 = 0
    '''
    def sendInitTimer():
        linkSafetyTimerFired = 1
        linkSafetyTimer.start()

    linkSafetyTimer = Timer(100.0, sendInitTimer)
    '''
    global readerRunning
    #linkSafetyTimer.start()
    #with serial.Serial("/dev/ttyS6", 115200, timeout=300) as ser:
    with serial.Serial("COM6", 115200, timeout=300) as ser:
        #sendInit()
        ser.write(coordInitStream)
        timeNow = time.time()
        linkSafetyTimer = timeNow
        while timeNow - tt < 30:
            #linkSafetyTimer.start()
            #linkSafetyTimerNew = time.time() - linkSafetyTimerOld
            if timeNow - linkSafetyTimer > 99: # should change this implementation to actuall timer
                ser.write(coordInitStream)
                linkSafetyTimer = timeNow
                
            if ser.inWaiting() > 0:
                #x = bytearray.fromhex(ser.read(ser.inWaiting()).encode('hex'))
                #for i in x:
                x = ser.read(ser.inWaiting())
                #if x[0] == bytearray.fromhex('10'):
                    #print("lolo")
                #print("len:", len(x), "-->", x, "<--")
                for i in x:
                    byteQueue.put(i)
                    #logger(i.encode('hex'),0)
            timeNow = time.time()
        ser.close()
        readerRunning = 0

    
thread_reader = Thread(target=reader)
thread_parser = Thread(target=parser)

thread_reader.start()
thread_parser.start()

thread_reader.join()
thread_parser.join()
