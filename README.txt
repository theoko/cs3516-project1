http_client.py
usage: http_client.py [-h] [--ttl]
                      serverURL [serverURL ...] serverPort [serverPort ...]

An HTTP client written in Python 2.7

positional arguments:
  serverURL   The server URL to perform a GET request
  serverPort  The server port

optional arguments:
  -h, --help  show this help message and exit
  --ttl       Prints the RTT for accessing the URL on the terminal before the
              server's response

This program uses the python socket library to create HTTP requests (TCP socket connections) to the server and port specified. If the ttl flag is specified, the program calculates the round trip time in milliseconds and displays it to the user. 

How to run:
“python http_client.py www.bbc.com 80”

“python http_client.py —ttl www.bbc.com 80”

=================

http_server.py
usage: http_server.py [-h] serverPort [serverPort ...]

An HTTP server written in Python 2.7

positional arguments:
  serverPort  The port to listen

optional arguments:
  -h, --help  show this help message and exit

This program uses python socket library to create an HTTP server to serve the contents of the directory and listen for connections on the port specified. If ‘/‘ is requested, the program will look for index.html or index.htm and if one of these files is found, the program will serve it. If another path is specified, the server will look for the requested file and display it if it is found. The server produces an HTTP 404 error if the requested file is not found.

The program implements multithreading. The program starts a new thread on each new connection and shuts down existing threads after the connection is closed. The program can be stopped by pressing Control-C. Before it stops executing, it shuts down every thread that is currently alive to make sure that the port that it is currently serving becomes available again. The server currently supports GET requests. The requested path and thread info is logged on the terminal.

How to run:
“python http_server.py 9000”
