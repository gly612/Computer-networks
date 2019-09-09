# -*- coding: utf-8 -*-
from socket import *
import sys
import os
import errno
import thread

# The entrance of the entire program, including create a server socket, bind to my ip and port number...
def main():
    # Create a server socket, bind it to a port and start listening
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    # implement port multiplexing
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_ip = sys.argv[1]
    tcpSerSock.bind((server_ip, 8888))
    tcpSerSock.listen(5)
    while 1:
        # Start receiving data from the client
        print ('Ready to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        # implement multi threading here
        thread.start_new_thread(proxy, (tcpCliSock, addr))
    # Close the server sockets
    tcpSerSock.close()


def proxy(tcpCliSock, addr):
    print ('Received a connection from: ', addr)
    message = tcpCliSock.recv(4096)
    
    # Extract the filename from the given message   
    try:
        filename = message.split()[1].partition("/")[2]
    except:
        pass
    
    print ('filename: ', filename)
    fileExist = "false"
    # is_file = true means that if there is 'Referer' tag in http request, browser is requiring files
    is_file = False
    true_host = filename

    messages = message.split("\n")
    for header in messages:
        # if there is 'Referer' tag in http request, it means the browser is requiring files, so we distinguish this situation with requiring a web page.
        if "Referer" in header:
            # true_host is the plain url, like: www.example.com
            true_host = header.split("/")[-1]
            true_host = true_host.strip()
            is_file = True
            break

    filetouse = "./" + true_host+"/"+filename
    print ('filetouse', filetouse)
    try:
        # Check wether the file exist in the cache
        f = open(filetouse, "r")

        fileExist = "true"
        # if_modified = true means that there is "Last-Modified" variable in the cache file
        if_modified = False
        outputdata = f.readlines()
        last_modified_time = ""
        for line in outputdata:
            # if there is "Last-Modified" variable in the cache file, we make if_modified=true and record the last modified time
            if "Last-Modified" in line:
                if_modified = True
                last_modified_time = line.replace("Last-Modified", "If-Modified-Since")
                break
        
        if if_modified:
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostn = true_host.replace("www.","",1)
            try:
                # Connect to the socket to port 80
                c.connect((hostn, 80))
                # Create a temporary file on this socket and ask port 80
                # for the file requested by the client
                fileobj = c.makefile('r', 0)
                if is_file:
                    fileobj.write("GET "+"http://" + true_host +"/" + filename+" HTTP/1.0\n"+last_modified_time+"\n") 
                else:
                    fileobj.write("GET "+"http://" + true_host + "/" +" HTTP/1.0\n"+last_modified_time+"\n") 
                
                my_buffer = fileobj.readline()
                # 200 means that the version of cache has been modified, so we update the cache and send the new cache back
                if "200" in my_buffer: 
                    tmpFile = open(filetouse,"wb")
                    tcpCliSock.send(my_buffer)
                    tmpFile.write(my_buffer)
                    buff = fileobj.readlines()
                    for line in buff:                                                     
                        tmpFile.write(line);                                               
                        tcpCliSock.send(line); 
                    tmpFile.close()
                # 304 means that the version of cache has not been modified, so we directly send the cache back
                if "304" in my_buffer: 
                        tcpCliSock.send(my_buffer)
                
                c.close()
            except Exception:
                print ("Illegal request")
                
        else:
            for line in outputdata:
                tcpCliSock.send(line)
 
        f.close()
        print ('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostn = true_host.replace("www.","",1)
            try:
                # Connect to the socket to port 80
                c.connect((hostn, 80))
                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                fileobj = c.makefile('r', 0) #Instead of using send and recv, we can use makefile

                # if is_file is true, it means we are requesting for files in the web.
                if is_file:
                    fileobj.write("GET "+"http://" + true_host +"/" + filename+" HTTP/1.0\nHost: "+ true_host+"\n\n") 
                else:
                    # if is_file is false, it means we simply request for the web page.(html)
                    fileobj.write("GET "+"http://" + true_host + "/" +" HTTP/1.0\nHost: "+ true_host+"\n\n") 
                # make a directory for all the cache files     
                if not os.path.exists(os.path.dirname(filetouse)):
                    try:
                        os.makedirs(os.path.dirname(filetouse))
                    except OSError as exc: 
                        # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                # Create a new file in the cache for the requested file.
                tmpFile = open(filetouse,"wb")


                # Read the response into buffer
                buff = fileobj.readlines()
                # Error handling for the 404 Not Found
                if not buff or len(buff) == 0:
                    tcpCliSock.send("HTTP/1.0 404 Not Found\r\n")
                    tcpCliSock.send("\r\n")
                    tcpCliSock.send("\r\n")
                # send the response in the buffer to client socket
                # and the corresponding file in the cache
                for line in buff:                                                     
                    tmpFile.write(line);                                               
                    tcpCliSock.send(line); 

                tmpFile.close()
                c.close()
            except Exception as e:
                print "Illegal request: "+str(e)
        else:
            # HTTP response message for file not found
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n")
            tcpCliSock.send("Content-Type:text/html\r\n")
            #Since we store both the header and the body of the http response, so there no possibility to have blank file. Thus we just pass the error handling.
    tcpCliSock.close()
        
    # Close the client
    tcpCliSock.close()
if __name__ == "__main__":
    main()