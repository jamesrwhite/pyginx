#
# A simple python web server, demo accessible at http://82.8.231.184:1337
#
# Author: James White
# URL: https://github.com/jamesrwhite/pyginx
# Date: 19/2/12
#
import socket, sys, thread
from time import gmtime, strftime

# Socket Setup
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("", 1337))
	sock.listen(5) 

except socket.error, (value, message):
	if sock: 
		sock.close() 

	print "Could not open socket: " + message 
	sys.exit(1)

# Function that handles accepting and returning
# data from clients
def handleClientConnections(client, address):
	# Get the client object and address
	stream = client.makefile(mode = "rw", bufsize = 1)

	# Store the HTTP headers sent by the client in a list
	headers = client.recv(4096)
	headers = headers.split("\n")

	# Get the HTTP Method and Path
	command = headers[0].split(" ")
	method = command[0]
	# If for some reason we don't get sent a Path
	# default it to /
	try :
		path = command[1]
	except IndexError :
		pass

	# Only accept GET requests
	if method != "GET":
		stream.write("HTTP/1.0 405 Unsupported\n")
		stream.write("Allow: GET\n")
		stream.write("Content-type: text/html\n")

		# Output the content
		stream.write("\n")
		stream.write("<pre><li>Request Method: " + method + "</li>")
		stream.write("<li>Path: " + path + "</li></pre>")
		stream.write("<h1>405 Unsupported</h1>")

	else:
		try:
			# Strip the / from the path
			path = path[1:]

			# If there is no path try and load index.html
			if len(path) == 0:
				path = "index.html"
			
			# Try to open the file specified by the path
			request_file = open("www/" + path, mode = "r")

			# Send the response HTTP headers
			stream.write("HTTP/1.0 200 OK\n")
			stream.write("Allow: GET\n")
			stream.write("Server: pyginx 0.1\n")

			# Add support for basic image
			def add_mime_type(path) :
				file_types = {
					"html" : "text/html",
					"jpg" : "image/jpg",
					"jpeg" : "image/jpg",
					"png" : "image/png",
					"gif" : "image/gif",
					"pdf" : "application/pdf"
				}

				# Add a file type if needed
				for file_type in file_types :
					if path.find(file_type) != -1 :
						return file_types[file_type]
			
			# Add the MIME Type to the file
			mime_type = str(add_mime_type(path))
			stream.write("Content-type: " + mime_type + "\n")
			stream.write("\n")

			if mime_type == "text/html" :
				# Output the content
				stream.write("<pre><li>Request Method: " + method + "</li>")
				stream.write("<li>Path: " + path + "</li></pre>")

			# Print out all lines in the file
			for line in request_file:
				stream.write(line)

		except IOError:
			# Send the HTTP Response headers
			stream.write("HTTP/1.0 404 Not Found")
			stream.write("Allow: GET\n")
			stream.write("Content-type: text/html\n")

			# Output the content
			stream.write("\n")
			stream.write("<pre><li>Request Method: " + method + "</li>")
			stream.write("<li>Path: " + path + "</li></pre>")
			stream.write("<h1>404 Not Found</h1>")
	
	# Print debug info
	print "Client: " + str(address)
	print "On Thread ID: " + str(thread_id)
	print "Request Time: " + strftime("%a, %d %b %Y %H:%M:%S", gmtime())
	print "Request File: " + path + "\n"

	# Close the connection
	stream.close()
	client.close()
	# thread.exit() Not sure whether to do this or not?

# Off we go!
while 1:
	# Get the client object and address
	client, address = sock.accept()

	# Start the thread
	thread_id = thread.start_new_thread(handleClientConnections, (client, address))