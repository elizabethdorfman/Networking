
# Elizabeth Dorfman
#Implementation of an HTTP server capable of handling GET and POST requests.

from socket import *
import threading
import time
import os
import urllib.parse


class Server:
    def __init__(self, addr, port, timeout):
        # Initialize instance varaiables
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.sessions = {}
        self.server_socket = socket(AF_INET, SOCK_STREAM)

        # Bind server socket to address port to listen on
        self.server_socket.bind((addr, port))
        self.server_socket.listen(5)

        # Set timeout
        self.server_socket.settimeout(self.timeout)

        # Track server connections
        self.server_on = True
        print(
            f"Server started on {self.addr}:{self.port} with a timeout of {self.timeout} seconds."
        )

    def start_server(self):
        # Run server indefinitely
        while self.server_on:
            try:
                connection, client_address = (
                    self.server_socket.accept()
                )  # Waits for a client to connect
                self.last_connection_time = (
                    time.time()
                )  # Updates the last connection time
                print(
                    f"Connection from {client_address} at {self.last_connection_time}."
                )
                thread = threading.Thread(
                    target=self.handle_request, args=(connection,)
                )  # Handles connection in new thread
                thread.start()  # Executes thread
            except timeout:  # Handles timeout exception
                print(
                    f"Server timed out– {self.timeout} second timeout period has passed."
                )
                self.stop_server()

    def stop_server(self):
        # Stop the server and close the socket.
        print("Stopping the server.")
        self.server_on = False
        self.server_socket.close()

    def parse_request(self, request_data):
        # Decode from bytes into string
        data = request_data.decode("utf-8")
        # parsing the raw HTTP request data request_data into request line, headers, and body by splitting it using the delimiter (\r\n)
        lines = data.split("\r\n")
        # The first line, known as the request line, contains the HTTP method, the requested path, and the HTTP version.
        request_line = lines[0]

        # Initialize headers and body
        headers = {}
        body = ""

        # For tracking whether collecting body lines
        in_body = False

        # Iterate through each line
        for line in lines[1:]:
            if line == "" or in_body == True:
                in_body = True
                body += line
            else:
                header = line.split(":", 1)
                key = header[0].strip()  # Strip any extra whitespace
                value = header[1].strip()  # Strip any extra whitespace
                headers[key] = value
        # The method returns the request line, headers, and body.
        return request_line, headers, body

    def handle_request(self, client_socket):
        # Receive the HTTP request data
        data = client_socket.recv(1024)

        # Check if empty test request and close socket
        if not data:
            client_socket.close()
            return

        # Extract request details
        request_line, headers, body = self.parse_request(data)
        try:
            method, path, version = request_line.split(" ")
        except:
            print(f"Malformed request line: {request_line}")
            method = "Invalid request"
        # Serve default page
        if path == "/" or not path:
            path = "assets/index.html"

        # Handle GET method
        if method == "GET":
            self.handle_get_request(client_socket, path)
        # Handle POST method
        elif method == "POST":
            self.handle_post_request(client_socket, path, headers, body)
        # Handle unsupported method
        else:
            print("Called unsupported request")
            self.handle_unsupported_method(client_socket, method)

        # Close the socket
        client_socket.close()

    def handle_unsupported_method(self, client_socket, method):
        # Create 405 page with unsupported method
        content = "<html><body><h1>405 Method Not Allowed</h1></body></html>"
        response_headers = (
            "HTTP/1.1 405 Method Not Allowed\r\n"
            f"Content-Length: {len(content)}\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
        )
        # Send response back to socket
        response = response_headers + content
        client_socket.sendall(response.encode("utf-8"))

    def handle_get_request(self, client_socket, file_path):
        # Retrieve client's name
        client_ip, client_port = client_socket.getpeername()
        print(f"Handling GET request to path {file_path}")
        try:
            client_name = self.sessions[client_ip]
        except:
            client_name = ""
        # Create http response to get file
        try:
            # Check if path exists
            os.path.exists(file_path)
            # Remove leading /
            file_path = file_path.lstrip("/")
            # Read file content and replace name
            with open(file_path, "r") as file:
                content = file.read()
                content = content.replace("{{name}}", client_name)
                # Create an http response header
                response_headers = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    "Content-Type: text/html\r\n"
                    "\r\n"
                )
        # 404 Exception if error opening file
        except:
            # Create 404 page with response headers
            content = "<html><body><h1>404 Not Found</h1></body></html>"
            response_headers = (
                "HTTP/1.1 404 Not Found\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
            )

        # Send response back to socket
        response = response_headers + content
        client_socket.sendall(response.encode("utf-8"))

    def handle_post_request(self, client_socket, path, headers, body):
        # Retrieving client name
        client_ip, client_port = client_socket.getpeername()
        print(f"Handling POST request from {client_ip}:{client_port}")

        # Parse body and get form data
        form_data = urllib.parse.parse_qs(body)
        path = path.lstrip("/")
        if path == "change_name":
            name = form_data["name"][0]
            print("Changing name to: ", name)
            self.sessions[client_ip] = name

            # Prepare HTTP response for name updating
            content = f"<html><body><h1>Name updated to {name}</h1></body></html>"
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
            )

        else:
            # Prepare HTTP response for 404 Error
            content = "<html><body><h1>Error: No POST data provided</h1></body></html>"
            response_headers = (
                "HTTP/1.1 404 Not Found\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
            )

        # Send response back to socket
        response = response_headers + content
        client_socket.sendall(response.encode("utf-8"))
