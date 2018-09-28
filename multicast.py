import socket
import struct
import sys
import random
import Queue
import pickle
import time
import threading
from time import sleep
from thread import *
from random import *

ACKcount = 0
filainicio = Queue.Queue()
filafinal = Queue.Queue()
pid = randint(0,10000)
tempo = 0
processcount = raw_input("Quantos processos deseja?")
processcount = int(processcount)
ACK = [[0 for i in range(processcount+1)] for y in range(processcount+1)]
ACK[0][1] = pid
ACK[1][0] = pid
MCAST_ADDR = "224.0.0.251"
MCAST_PORT = 1050

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

group = socket.inet_aton(MCAST_ADDR)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

sock.bind(("224.0.0.251", 1050))

def sender():
    mensagem = str(tempo) + "/" + str(pid) + "/" + "Sistemas distribuidos"
    sock.sendto(mensagem, ("224.0.0.251", 1050))
        

def receiver():
    while ACKcount < processcount:
        data = sock.recv(1024)
        msgsplit = data.split("/")
        if(msgsplit[2] != "ACK"):
            enfileirar = (msgsplit[0], msgsplit[1])
            filainicio.put(enfileirar)
        aux = 1
        for aux in range(processcount+1):
            if(ACK[aux][0] == msgsplit[1]):
                break
            elif(ACK[aux][0] == 0):
                ACK[aux][0] = msgsplit[1]
                ACK[0][aux] = msgsplit[1]

        print (list(filainicio.queue))
        if(msgsplit[2] != "ACK"):
            ACKmsg = str(tempo) + "/" + str(pid) + "/" + "ACK"
            sock.sendto(ACKmsg, ("224.0.0.251", 1050))        
        else:
            aux = 1
            for aux in range(processcount+1):
                if(ACK[aux][0] == msgsplit[1]):
                    arcorx = aux
                    break
            aux = 1
            for aux in range(processcount+1):
                if(ACK[0][aux] == pid):
                    arcory = aux
                    break
            ACK[arcorx][arcory] = 1
            aux = 1
            for aux in range(processcount+1):


if __name__ == '__main__':
    r = threading.Thread(target = receiver)
    s = threading.Thread(target = sender)
    r.daemon = True
    s.daemon = True
    r.start()
    time.sleep(5)
    s.start()
    while True:
        time.sleep(1)
    # if(sys.argv[1] == "receiver"):
    #     receiver()
    # elif(sys.argv[1] == "sender"):
    #     sender()
    # else:
    #     exit("Specify 'sender' or 'receiver'")
    