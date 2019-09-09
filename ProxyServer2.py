from socket import *
import sys

if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
	sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerPort = 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('', tcpSerPort))
tcpSerSock.listen(1)
# Fill in start.
# Fill in end.

while 1:
	# Start receiving data from the client
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('Received a connection from:', addr)
	message = tcpCliSock.recv(4096).decode()
	print(message)
	# Extract the filename from the given message
	# print(message.split()[1])
	# filename = message.split()[1].partition("/")[2]
	filename = message.split()[1].partition("//")[2].replace('/', '_')
	print(filename)
	fileExist = "false"
	# filetouse = "/" + filename
	# print(filetouse)
	try:
		# Check wether the file exist in the cache
		# f = open(filetouse[1:], "r")
		f = open(filename, "r")
		outputdata = f.readlines()
		fileExist = "true"
		# ProxyServer finds a cache hit and generates a response message
		# tcpCliSock.send("HTTP/1.0 200 OK\r\n")
		# tcpCliSock.send("Content-Type:text/html\r\n")
		for i in range(0, len(outputdata)):
			tcpCliSock.send(outputdata[i].encode())
		print('Read from cache')
	# Error handling for file not found in cache
	except IOError:
		if fileExist == "false":
			# Create a socket on the proxyserver
			c = socket(AF_INET, SOCK_STREAM)
			# hostn = filename.replace("www.","",1)
			hostn = message.split()[1].partition("//")[2].partition("/")[0]
			print(hostn)
			try:
				# Connect to the socket to port 80
				c.connect((hostn, 80))
				print('Socket connected to port 80 of the host')
				# Create a temporary file on this socket and ask port 80 for the file requested by the client
				c.sendall(message.encode())
				buff = c.recv(4096)
				tcpCliSock.sendall(buff)
				# Create a new file in the cache for the requested file.
				# Also send the response in the buffer to client socket and the corresponding file in the cache
				tmpFile = open("./" + filename,"w")
				tmpFile.writelines(buff.decode().replace('\r\n', '\n'))
				tmpFile.close()
			except:
				print("Illegal request")
		else:
			# HTTP response message for file not found
			header = ' HTTP/1.1 404 Found'
			tcpCliSock.send(header.encode())
			# Fill in start.
			# Fill in end.
	# Close the client and the server sockets
	tcpCliSock.close()
tcpSerSock.close()
# Fill in start.
# Fill in end.
