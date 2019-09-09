#!/usr/bin/env python 
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)  # socket()
serverSocket.bind(('', serverPort))         # bind() 
print ("The server is ready to receive")
while True:
    message, clientAddress = serverSocket.recvfrom(2048) # recv()
    modifiedMessage = message.decode().upper()           
    serverSocket.sendto(modifiedMessage.encode(),clientAddress) # send() 

serverSocket.close() #close() 