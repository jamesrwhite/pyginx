#
# A simple python web server
#
# Author: James White
# Date: 12/2/12
#
import socket, sys, threading

# Socket Setup
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', 1343))
	sock.listen(5)

except socket.error, (value, message):
	if sock: 
		sock.close() 

	print 'Could not open socket: ' + message 
	sys.exit(1)

# Function that handles accepting and returning
# data from clients
def handleClientConnections():
	# Get the client object and address
	client, address = sock.accept()
	stream = client.makefile(mode = 'rw')

	# Store the HTTP headers sent by the client in a list
	headers = client.recv(4096)
	headers = headers.split('\n')

	# Get the HTTP Method and Path
	command = headers[0].split(' ')
	method = command[0]
	path = command[1]

	# Only accept GET requests
	if method != 'GET':
		stream.write('HTTP/1.0 405 Unsupported\n\nUnsupported Method')
		stream.write('Allow: GET\n')

	else:
		try:
			# Strip the / from the path
			path = path[1:]

			# If there is no path try and load index.html
			if len(path) == 0:
				path = 'index.html'
			
			# Try to open the file specified by the path
			request_file = open(path, mode = 'r')

			# Send the response HTTP headers
			stream.write('HTTP/1.0 200 Success\n')
			stream.write('Allow: GET\n')
			stream.write('Content-type: text/html\n')

			# Output the content
			stream.write('\n')
			stream.write('<pre><li>Request Method: ' + method + '</li>')
			stream.write('<li>Path: ' + path + '</li></pre>')

			# Print out all lines in the file
			for line in request_file:
				stream.write(line)

		except IOError:
			# Send the HTTP Response headers
			stream.write('HTTP/1.0 404 Not Found')
			stream.write('Allow: GET\n')
			stream.write('Content-type: text/html\n')

			# Output the content
			stream.write('\n')
			stream.write('<pre><li>Request Method: ' + method + '</li>')
			stream.write('<li>Path: ' + path + '</li></pre>')
			stream.write('<h1>404 Not Found</h1>')

	# Close the connection
	stream.close()
	client.close()

# Off we go!
while 1:
	handleClientConnections()