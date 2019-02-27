import sys
import argparse
import socket
import threading
import time
import os.path


def stop_threads_and_exit(threads):
    for i in range(0, len(threads)):
        if threads[i].isAlive():
            print("Shutting down thread with ID %d" % i)
            while threads[i].isAlive():
                try:
                    threads[i].socket_conn.close()
                except IOError:
                    threads[i].stop()
                if threads[i].isAlive():
                    print("Waiting 10 seconds for connections to close...")
                    time.sleep(10)
                if not(threads[i].isAlive()):
                    break
                threads[i].join(30)
                print("Waiting for threads to shut down and freeing resources...")
                if not(threads[i].isAlive()):
                    break
                threads[i].stop()  # Signal the event
                if not(threads[i].isAlive()):
                    break
                threads[i].join()
    print("Exiting...")
    time.sleep(5)  # The listening port should now become available
    sys.exit()


class ServeClient (threading.Thread):

    def __init__(self, threadid, buffersize, socket_conn, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.buffsize = buffersize
        self.socket_conn = socket_conn
        self.addr = addr
        self.port = port
        self._stop_event = threading.Event()

    def send_ok_headers(self):
        try:
            # Send 200 OK
            self.socket_conn.send(bytes("HTTP/1.1 200 OK\r\n"))

            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

            # Send headers
            self.socket_conn.send(bytes('Date: {now}\n'.format(now=time_now)))
            self.socket_conn.send(bytes('Server: HTTP Python Server\n'))
            self.socket_conn.send(bytes('Connection: close\n\n'))
        except IOError:
            self.stop()

    def send_not_found_headers_and_close(self, msg="File not found"):
        try:
            # Send 404 NOT FOUND
            self.socket_conn.send(bytes("HTTP/1.1 404 Not Found\r\n\r\n"))
            self.socket_conn.send(bytes(msg))
        except IOError:
            self.stop()

    def read_and_display_file(self, filename):
        try:
            # Try reading file
            f = open(filename, 'r')

            # Send message in chunks
            for line in f.readlines():
                self.socket_conn.send(bytes(line))

            f.close()
        except IOError:
            self.send_not_found_headers_and_close()

    def get_file(self, file_path):

        # Log requested path to terminal
        print("Requested path: /%s (request ID: %d)" % (file_path, self.threadID))

        if file_path == '' or file_path == '/':
            # Log
            print("Checking default file names to serve")

            # Check default locations
            if os.path.isfile('index.html'):
                self.send_ok_headers()
                self.read_and_display_file('index.html')
            elif os.path.isfile('index.htm'):
                self.send_ok_headers()
                self.read_and_display_file('index.htm')
            else:
                self.send_not_found_headers_and_close("Default file index.html not found on server")
        else:

            if os.path.isfile(file_path):
                # Send 200 OK if requested file exists
                self.send_ok_headers()
                # Read and display file
                self.read_and_display_file(file_path)
            else:
                self.send_not_found_headers_and_close()

        return True

    def run(self):
        # Parse headers
        get_req = self.socket_conn.recv(self.buffsize).decode()

        try:
            # Try to get request path
            req_path = get_req.split()[1]
        except IndexError:
            req_path = '/'

        # GET request
        if get_req.find("GET") != -1:
            if os.path.isfile(req_path):
                # Get file
                self.get_file(req_path)
            else:
                # Remove first '/'
                req_path = req_path[1: len(req_path)]

                # Try to get requested file contents
                self.get_file(req_path)
        else:
            try:
                self.socket_conn.send(bytes("Unrecognized request"))
            except IOError:
                self.stop()

        # Shut down thread
        self.socket_conn.close()
        self.stop()

        # Sleep for 10 seconds to demonstrate that we can handle multiple connections by starting more threads
        # time.sleep(10)

    def stop(self):
        try:
            self.socket_conn.close()
        except IOError:
            print("Socket closed (%d)" % self.threadID)
        self._stop_event.set()

    def thread_stopped(self):
        return self._stop_event.is_set()


if __name__ == "__main__":
    # Provide program description and help
    parser = argparse.ArgumentParser(description='An HTTP server written in Python 2.7')
    parser.add_argument('serverPort', metavar='serverPort', type=int, nargs='+',
                            help='The port to listen')

    # Parse arguments
    args = parser.parse_args()

    # Parse server port from user input
    server_port = args.serverPort[0]

    # Initialize a socket for the HTTP server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Serve at specified port
    server_sock.bind(('', server_port))

    # Allow 20 connections to be queued
    server_sock.listen(10)

    # Thread ID
    thread_id = 0

    # Threads list
    threads_started = []
    threads_alive = []
    threads_stopped = []

    # Buffer size
    buffer_size = 1024

    # Clients served
    clients = {}

    # Print message to the user
    print("Listening for connections on port: %d" % server_port)

    while True:
        try:
            # Accept incoming connection
            server_conn, address = server_sock.accept()

            if address[1] in clients:
                clients[address[1]] = True
            else:
                # Initialize a thread object and add it to the list of started threads
                threads_started.append(
                    ServeClient(thread_id, buffer_size, server_conn, address, server_port)
                )

                # Start a new thread to handle a connection
                threads_started[thread_id].start()

                # Check for dead threads and remove them
                for tid in range(0, thread_id):
                    if not (threads_started[tid].isAlive()):
                        # Append to threads_stopped
                        threads_stopped.append(threads_started[tid])
                        if threads_started[tid] in threads_alive:
                            threads_alive.remove(threads_started[tid])
                    else:
                        threads_alive.append(threads_started[tid])

                # Display stats every 15 threads
                if thread_id % 15 == 0:
                    print("Info: %d threads in total." % threading.active_count())

                # Increment thread_id to keep track of the threads have been instantiated
                thread_id += 1
        except (KeyboardInterrupt, SystemExit):
            stop_threads_and_exit(threads_started)