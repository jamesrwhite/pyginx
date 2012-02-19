#
# A simple python web server
#
# Author: James White
# Date: 12/2/12
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
	try :
		path = command[1]
	except IndexError :
		path = "/"

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
			request_file = open(path, mode = "r")

			# Send the response HTTP headers
			stream.write("HTTP/1.0 200 Success\n")
			stream.write("Allow: GET\n")

			# Add support for basic image
			def check_if_image(path) :
				image_types = {
					"jpg" : "image/jpg",
					"jpeg" : "image/jpg",
					"png" : "image/png",
					"gif" : "image/gif"
				}

				for image_type in image_types :
					if path.find(image_type) != -1 :
						return image_types[image_type]
				
				return False
			
			# Equal to Image MIME Type or False
			is_image = check_if_image(path)

			if is_image :
				stream.write("Content-type: " + is_image + "\n")
				stream.write("\n")
			
			else :
				# Otherwise assume text/HTML Content
				stream.write("Content-type: text/html\n")

				# Output the content
				stream.write("\n")
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

	# Close the connection
	stream.close()
	client.close()

# Off we go!
while 1:
	# Get the client object and address
	client, address = sock.accept()

	# Start the thread
	thread_id = thread.start_new_thread(handleClientConnections, (client, address))

	# Print debug info
	print "Client: " + str(address)
	print "On Thread ID: " + str(thread_id)
	print "Request Time: " + strftime("%a, %d %b %Y %H:%M:%S", gmtime()) + "\n"