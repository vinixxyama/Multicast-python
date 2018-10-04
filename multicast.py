# - Alunos:
#       Henrique Kodama RA:726537
#       Vinicius Yamamoto RA:490105
#
# - Disciplina:
#       Sistemas Distribuidos
#
# - Professo:
#       Fabio Verdi
#
# - UFSCar Sorocaba

# ------ Libraries ------ #
import config
import mod
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

# ------ Global Variables ------ #
ACKcount = 0
InitialQueue = Queue.Queue()
FinalQueue = Queue.Queue()
pid = randint(0,10000)
tickRate = raw_input("Define the tick rate: ")
processcount = raw_input("Quantos processos deseja? ")
processcount = int(processcount)
ACK = [[0 for i in range(processcount+1)] for y in range(processcount+1)]
ACK[0][1] = pid
ACK[1][0] = pid
MCAST_ADDR = "224.0.0.251"
MCAST_PORT = 1050

# AF_INET: Specifies the use of (host, port) pair
# SOCK_DGRAM: Socket type, datagram
# IPPROTO_UDP: UDP Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# iinet_aton(): Convert the given address to 32-bit binary format
group = socket.inet_aton(MCAST_ADDR)

# INADDR_ANY: Bind socket to all local interfaces
mreq = struct.pack('4sL', group, socket.INADDR_ANY)

# IP_ADD_MEMBERSHIP: join the local multicast group
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# SO_REUSEADDR: Allow reuse of local address
# SO_REUSEPORT: Allow multiple sockets to be bound to same address
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# IP_MULTICAST_LOOP: Loop the message to yourself
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

# Binds the socket
sock.bind(("224.0.0.251", 1050))

# ------ Functions ------ #

def sender():
    while True:
        opcao = raw_input("Deseja enviar uma mensagem? ")

        if(int(opcao) == 1):
            # Input the message
            message = raw_input("Type in your message: ")

            # Concatenate the clock, PID and message
            mensagem = str(config.clock) + "/" + str(pid) + "/" + str(message)

            # multicast the message to the given address
            sock.sendto(mensagem, ("224.0.0.251", 1050))
        if(int(opcao) == 2):
            print(list(FinalQueue.queue))
        elif(int(opcao) == 0):
            exit()


def receiver():
    print(">>>>> LISTENING <<<<<")    
    # Receive loop
    while True:
        data = sock.recv(1024)

        # Split the message from the clock/PID/message form
        msgsplit = data.split("/")

        # Update the clock (Lamport's logical clock)
        if(int(config.clock) + int(tickRate) < int(msgsplit[0])):
            print("Updated clock to " + msgsplit[0])
            config.clock = int(msgsplit[0]) + 1

        # Cast to check the ACK matrix
        msgsplit[1] = int(msgsplit[1])

        # Loop to see if the sender PID is already known
        for aux in range(1, processcount + 1):
            # If its known
            if(ACK[aux][0] == msgsplit[1]):
                break

            # If not known, add it to the matrix
            else:
                if(ACK[aux][0] == 0):
                    ACK[aux][0] = msgsplit[1]
                    ACK[0][aux] = msgsplit[1]
                    break

        # If an ordinary message is received
        if(msgsplit[2] != "ACK"):
            # Create the tuple to be queued (clock, PID)
            msg = (msgsplit[0], msgsplit[1])
            InitialQueue.put(msg)

            # Create the ACK message to multicast
            ACKmsg = str(config.clock) + "/" + str(pid) + "/" + "ACK"
            sock.sendto(ACKmsg, ("224.0.0.251", 1050))

        # If it is an ACK
        else:
            # Find the given spot receiverXsender on the matrix
            for aux in range(1,processcount+1):
                if(ACK[aux][0] == msgsplit[1]):
                    row = aux
                    break
            for aux in range(1,processcount+1):
                if(ACK[0][aux] == pid):
                    column = aux
                    break

            # Insert 1 on the given position, indicating an ACK was received
            ACK[row][column] = 1
            recebido = 1

            # Check if for that column (sender), all ACKS were received
            for aux in range(1, processcount+1):
                if(ACK[aux][column] == 0):
                    recebido = 0

            # If all of them were received
            if(recebido == 1):
                # Change all the 1's to 0's
                for aux in range(1, processcount + 1):
                    ACK[aux][column] = 0
                retorno = InitialQueue.get()

                # Insert into FinalQueue for verification
                FinalQueue.put(retorno)
                print("\nMensagem do process com PID " + str(retorno[1])
                       + " foi passada para a camada superior\n")



def clockUpdate():
    while(True):
        time.sleep(0.5)
        config.clock = config.clock + int(tickRate)

if __name__ == '__main__':
    r = threading.Thread(target = receiver)
    s = threading.Thread(target = sender)
    t = threading.Thread(target = clockUpdate)

    r.daemon = True
    s.daemon = True
    t.daemon = True

    r.start()
    t.start()
    s.start()

    while True:
        time.sleep(1)

    
