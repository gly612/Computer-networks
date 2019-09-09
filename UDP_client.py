#!/usr/bin/env python 
from socket import *

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM) # socket()
message = raw_input('Input lowercase sentence:') 
clientSocket.sendto(message.encode(),(serverName, serverPort)) # send()
modifiedMessage, serverAddress = clientSocket.recvfrom(2048) # receive()
print(modifiedMessage.decode())
clientSocket.close() # close()