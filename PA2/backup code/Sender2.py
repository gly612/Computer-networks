from socket import *
import sys
import time
import utils



MAX_SIZE = 500
WND_SIZE = 15
ssthread = 8


TIME_OUT = 0.5

def send(file_content, serverSocket, receiver_address, receiver_port, ack_signal):
    send_base = 0
    next_seq = 0
    global WND_SIZE
    global ssthread
    print("file length", len(file_content))
    while True:

        if next_seq < send_base + WND_SIZE and next_seq < len(file_content): # When not reaching to the window end, send the packet
            print("current sequence = {}, current base = {}".format(next_seq, send_base))
            packet_to_send = utils.make_packet(next_seq, file_content[next_seq][0], file_content[next_seq][1])
            serverSocket.sendto(packet_to_send, (receiver_address, receiver_port))
            next_seq = (next_seq + 1) & 0xffffffff
        try:
            recv_seq = recv(serverSocket, receiver_address, receiver_port, ack_signal, file_content) # Receive acknowledgement
            print("current window size ", WND_SIZE)
        except KeyboardInterrupt: # Could stop from keyboard
            exit()
        else:
            if WND_SIZE < ssthread:
                WND_SIZE = WND_SIZE * 2
            else:
                WND_SIZE = WND_SIZE + 1
        if recv_seq and recv_seq < send_base + WND_SIZE: # Move the window
            send_base = recv_seq
        else:
            next_seq = send_base

        if send_base == len(file_content): # When reach to the end
            break


def read_file(file):
    file_content = []
    file_iter = utils.read_file(file)
    data = file_iter.next()
    file_content.append([data, 0])

    while True:
        try:
            data = file_iter.next()  # generate next chunk
            file_content.append([data, 1])  # invoked by data from above
        except StopIteration:
            print('file reached end')
            break
    return file_content




# @timeout_decorator.timeout(TIME_OUT)
def recv(recvsocket, receiver_address, receiver_port, ack_signal, file_content):
    global WND_SIZE
    global ssthread #thresheld
    recvsocket.settimeout(TIME_OUT)
    try:
        while True:
            recv_packet, (address, port) = recvsocket.recvfrom(MAX_SIZE)
            csum, rsum, seqnum, flag, data = utils.extract_packet(recv_packet)

            if csum == rsum:
                ack_signal[seqnum - 1] += 1
                if ack_signal[seqnum - 1] == 3: # Retransmission determine
                    ack_signal[seqnum - 1] = 0
                    packet = utils.make_packet(seqnum, file_content[seqnum][0], file_content[seqnum][1])
                    recvsocket.sendto(packet, (receiver_address, receiver_port))
                    print ("retransmission triggered")
                    ssthread = WND_SIZE // 2
                    WND_SIZE = ssthread
                return seqnum
            else:
                return None
    except timeout:
        ssthread = ssthread // 2
        WND_SIZE = 1
    except:
        return None

# def main():
    # if len(sys.argv) < 4:
    #     sys.exit(-1)
    # file_name = sys.argv[1]
    # receiver_address = sys.argv[2]
    # receiver_port = int(sys.argv[3])
    # serverSocket = socket(AF_INET, SOCK_DGRAM)  # socket()
    # file_content = read_file(file_name)
    # ack_signal = []
    # for i in range(0, len(file_content)):
    #     ack_signal.append(0)
    # try:
    #     send(file_content, serverSocket, receiver_address, receiver_port, ack_signal)
    # except (KeyboardInterrupt, SystemExit):
    #     exit()



if __name__ == '__main__':
    try:
	    # main()
        if len(sys.argv) < 4:
            sys.exit(-1)
        file_name = sys.argv[1]
        receiver_address = sys.argv[2]
        receiver_port = int(sys.argv[3])
        serverSocket = socket(AF_INET, SOCK_DGRAM)  # socket()
        file_content = read_file(file_name)
        ack_signal = []
        for i in range(0, len(file_content)):
            ack_signal.append(0)
        try:
            send(file_content, serverSocket, receiver_address, receiver_port, ack_signal)
        except (KeyboardInterrupt, SystemExit):
            exit()

    except(KeyboardInterrupt, SystemExit):
        exit()
