import argparse
import socket
import time


def host_exists(host):
    """
    This function checks if a given name resolves to an IP address
    It returns True if it resolves and False otherwise
    """
    try:
        socket.gethostbyname(host)
        return True
    except socket.error:
        return False


def server_path(url):
    """
    This function parses the path for the given complete URL
    It returns a tuple containing the parsed host name and path for the given URL
    """
    hostname = url

    # Omit "http" or "https"
    if url.startswith('http://'):
        hostname = url[7:len(url)]
    elif url.startswith('https://'):
        hostname = url[8:len(url)]

    # Set a default path
    request_path = '/'

    # Check if the user has specified a path
    path_splitter = hostname.find('/')

    # If a path is specified, replace the default path and remove it from the host name
    if path_splitter != -1:
        request_path = hostname[path_splitter:len(hostname)]
        hostname = hostname[0:path_splitter]

    # Return a tuple containing hostname and path
    return hostname, request_path


def open_socket(url, port, rtt):
    # Buffer size for the server response
    buffer_size = 512

    # Get the hostname and the path
    # server_details is a list containing the hostname as the first entry and the server path as the second entry
    server_details = [server_path(url)[0], server_path(url)[1]]

    if not(host_exists(server_details[0])):
        print("The host that you specified does not exist. Please check your input and try again.")
        return

    # Check if --ttl was specified
    if rtt:
        # Start the timer in case --ttl is specified
        start_time = time.time()

    # Open socket
    # We are expecting a TCP packet
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set socket timeout
    tcp_socket.settimeout(10)

    # Create tuple with url and port
    tcp_socket.connect((server_details[0], port))

    # Send a GET request (HTTP 1.1)
    request = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\nUser-agent: HTTPClient\r\n\r\n" \
              % (server_details[1], server_details[0])

    # Encode the request and send the request data to the server
    tcp_socket.send(request.encode())

    # Store the response that we get from the server
    server_response = tcp_socket.recv(buffer_size)

    if rtt:
        # Stop the timer
        stop_time = time.time()

        # Calculate time difference to find RTT
        rtt = str(
            int(round((stop_time - start_time) * 1000, 0))
        )

        # Print the RTT in milliseconds
        print("RTT: %s MS" % rtt)

    # Print the response that we got from the server
    print("Response: ", server_response.decode())

    # Close the connection
    tcp_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='An HTTP client written in Python 2.7')
    parser.add_argument('--ttl', action='store_true',
                        help='Prints the RTT for accessing the URL on the terminal before the server\'s response')
    parser.add_argument('serverURL', metavar='serverURL', type=str, nargs='+',
                        help='The server URL to perform a GET request')
    parser.add_argument('serverPort', metavar='serverPort', type=int, nargs='+',
                        help='The server port')

    args = parser.parse_args()

    # Server URL: args.serverURL
    # Server Port: args.serverPort
    # TTL: args.ttl (True | False)
    print("Requested: %s" % server_path(args.serverURL[0])[0])
    print("Port: %d" % args.serverPort[0])

    open_socket(args.serverURL[0], args.serverPort[0], args.ttl)
