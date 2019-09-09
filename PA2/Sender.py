from socket import *
import sys
import time
from utils import *



MAX_SIZE = 500
WND_SIZE = 10
TIME_OUT = 0.5
win_begin=0

# This function is to send packets to the receiver
def send(file_to_send, serverSocket, receiver_address, receiver_port, acks):
    global win_begin
    next_seq = 0
    while True:
        # If not reaching the end of the window, then we send the packet to receiver
        if next_seq < win_begin + WND_SIZE and next_seq < len(file_to_send): 
            packet_send_to_receiver = make_packet(next_seq, file_to_send[next_seq][0], file_to_send[next_seq][1])
            serverSocket.sendto(packet_send_to_receiver, (receiver_address, receiver_port))
            next_seq = (next_seq + 1) & 0xffffffff
        try:
            # ger ack info from receiver
            recv_seq = recv(serverSocket, receiver_address, receiver_port, acks, file_to_send)
        except KeyboardInterrupt: 
            exit()

        serverSocket.settimeout(None)

        # Here we move the window
        if recv_seq and recv_seq < win_begin + WND_SIZE: 
            win_begin = recv_seq

        else:
            next_seq = win_begin
        # When reaching the end
        if win_begin == len(file_to_send): 
            break


# receive ack packet from the receiver
def recv(recvsocket, receiver_address, receiver_port, acks, file_to_send):
    # set a 500ms timeout 
    recvsocket.settimeout(TIME_OUT)
    try:
        while True:
            recv_packet, (address, port) = recvsocket.recvfrom(MAX_SIZE)
            #extracting the contents of the packet, with a method from utils
            csum, rsum, seqnum, flag, data = extract_packet(recv_packet)

            if csum == rsum:
                acks[seqnum - 1] += 1
                # If there is 3 duplicate acks, then fast retransmission
                if acks[seqnum - 1] == 3: 
                    acks[seqnum - 1] = 0
                    packet = make_packet(seqnum, file_to_send[seqnum][0], file_to_send[seqnum][1])
                    recvsocket.sendto(packet, (receiver_address, receiver_port))
                    # print ("Retransmission is triggered !")
                return seqnum
            else:
                return None
    # if timeout happens, retransmit the oldest one
    except timeout:
        oldest_packet = make_packet(win_begin, file_to_send[win_begin][0], file_to_send[win_begin][1])
        recvsocket.sendto(oldest_packet, (receiver_address, receiver_port))
    except:
        return None
        

# Get all the trunks
def read(file_name):
    file_to_send = []
    #extracting one trunk, with a method from utils
    chunk = read_file(file_name)
    data = chunk.next()
    # put the trunk data into a list
    file_to_send.append([data, 0])

    while True:
        try:
            # get the next trunk
            data = chunk.next()  
            file_to_send.append([data, 1]) 
        except StopIteration:
            # print('file reached end')
            break
    return file_to_send





if __name__ == '__main__':
    try:
        if len(sys.argv) < 4:
            sys.exit(-1)
        file_name = sys.argv[1]
        receiver_address = sys.argv[2]
        receiver_port = int(sys.argv[3])
        #create UDP socket
        serverSocket = socket(AF_INET, SOCK_DGRAM)  
        file_to_send = read(file_name)
        # ack list used to check duplicate acks
        acks = []
        for i in range(0, len(file_to_send)):
            acks.append(0)
        try:
            send(file_to_send, serverSocket, receiver_address, receiver_port, acks)
        except (KeyboardInterrupt, SystemExit):
            exit()
    except(KeyboardInterrupt, SystemExit):
        exit()
