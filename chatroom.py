import socket
import threading  # For threads
import sys  # for print
import readline  # For handling the input buffer
import time  # For shutdown
import select  # For blocking calls
import traceback


class ServerTCP:
    def __init__(self, server_port):
        print("TCP CHATROOM\nThis is the server side.")
        self.server_port = server_port
        self.address = socket.gethostbyname(socket.gethostname())
        # Initialize clients dictionary
        self.clients = {}
        # New thread event for server's running state
        self.run_event = threading.Event()
        # New thread event for server's message handling state
        self.handle_event = threading.Event()
        # Store threads in list

        # Initialize socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.address, self.server_port))
        self.server_socket.listen(5)

    def accept_client(self):
        try:
            # check if message has been sent
            ready, _, _ = select.select(
                [self.server_socket], [], [], 1
            )  # 1 second timeout
            if ready:
                connection, _ = self.server_socket.accept()
                name = connection.recv(1024).decode("utf-8")
                # Check if name is in the client list
                if name in self.clients.values():
                    message = "Name already taken."
                    connection.send(message.encode("utf-8"))
                    return False
                else:
                    message = "Welcome"
                    connection.send(message.encode("utf-8"))
                    self.clients[connection] = name
                    self.broadcast(connection, "join")
                    return True
        except Exception as e:
            print(f"Socket error: {e}")
            return False

    def close_client(self, client_socket):
        try:
            if client_socket in self.clients:
                client_name = self.clients.pop(client_socket)
                client_socket.close()
                return True
        except Exception as e:
            print(f"Error at close_client(): {e}")
        return False

    def broadcast(self, client_socket_sent, message):
        name = self.clients.get(client_socket_sent, "Unknown")
        if message == "join":
            broadcast_message = f"User {name} joined"
        elif message == "exit":
            broadcast_message = f"User {name} left"
        else:
            broadcast_message = f"{name}: {message}"

        for i in list(self.clients.keys()):
            if i != client_socket_sent:
                try:
                    i.send(broadcast_message.encode("utf-8"))
                except Exception as e:
                    print(f"Error at broadcast(): {e}.")

    def shutdown(self):
        try:
            self.run_event.set()
            self.handle_event.set()
            time.sleep(1)
            print("Shutting down...")
            for i in list(self.clients.keys()):
                i.send("server-shutdown".encode("utf-8"))
                self.close_client(i)
            # Wait for all client-handling threads to finish

            self.server_socket.close()

        except Exception as e:
            print(f"Error shutting down the server: {e}")
            self.run_event.set()
            self.handle_event.set()
            self.server_socket.close()

    def get_clients_number(self):
        return len(self.clients)

    def handle_client(self, client_socket):

        while not self.handle_event.is_set():
            try:
                if select.select([client_socket], [], [], 1)[0]:
                    message = client_socket.recv(1024).decode("utf-8")
                    self.broadcast(client_socket, message)
                    if message == "exit":
                        break

            except Exception as e:
                print(f"Error:{e}")
                break
        self.close_client(client_socket)
        # self.handle_event.set()

    def run(self):
        print(
            f"Launching chatroom server on address: {self.address} and port number: {self.server_port}"
        )
        print("Press CTRL+C to shut down the server.")
        print("Waiting for users to join...")
        while not self.run_event.is_set():
            try:
                # Try to accept a client connection
                if self.accept_client():
                    client_socket = list(self.clients.keys())[-1]
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket,)
                    )
                    client_thread.start()
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Catch any other exceptions within the loop
                break
        self.run_event.set()
        self.shutdown()


class ClientTCP:
    def __init__(self, client_name, server_port):
        print("TCP CHATROOM\nThis is the client side.")

        # Initialize instance variables and threading events
        self.client_name = client_name
        self.prompt = f"{self.client_name}: "
        self.server_addr = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = server_port
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event()

    def connect_server(self):
        try:
            self.client_socket.connect((self.server_addr, self.server_port))
            self.client_socket.send(self.client_name.encode("utf-8"))

            response = self.client_socket.recv(1024).decode("utf-8")
            print(f"{response}")
            if "Welcome" in response:
                return True
            else:
                print("Error: Name already taken.")
                # self.client_socket.close()
                return False
        except Exception as e:
            print(f"Connection error: {e}")
        return False

    def send(self, text):
        try:
            self.client_socket.send(text.encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")

    def receive(self):
        while not self.exit_receive.is_set():
            try:
                ready, _, _ = select.select(
                    [self.client_socket], [], [], 1
                )  # 1 second timeout
                if ready:
                    message = self.client_socket.recv(1024).decode("utf-8")
                    if "server-shutdown" == message:
                        self.exit_receive.set()
                        self.exit_run.set()
                        break

                    sys.stdout.write("\r" + " " * (len(self.client_name + ": ")) + "\r")

                    # 2. Print out the incoming message
                    print(f"{message}")

                    # 3. Rewrite the last line (prompt)
                    sys.stdout.write(self.prompt)

                    sys.stdout.flush()  # Ensure the prompt is printed immediately
                    readline.redisplay()  # redisplay what the user was typing
            except Exception as e:
                print(f"General error: {e}")
                self.exit_run.set()
                self.exit_receive.set()
                break  # Break the loop if there's an error
        self.client_socket.close()

    def run(self):
        if self.connect_server():
            receive_thread = threading.Thread(target=self.receive, args=())
            receive_thread.start()
            while not self.exit_run.is_set():
                try:
                    message = input(self.prompt)
                    self.send(message)
                    if message == "exit":
                        break
                except KeyboardInterrupt:
                    break

        self.exit_run.set()
        self.exit_receive.set()


class ServerUDP:
    def __init__(self, server_port):
        print("UDP CHATROOM\nThis is the server side.")
        self.server_port = server_port
        self.address = socket.gethostbyname(socket.gethostname())
        # Initialize clients dictionary
        self.clients = {}
        # Initialize messages list
        self.messages = []
        # New thread event for server's running state
        self.run_event = threading.Event()
        # Initialize socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.address, self.server_port))
        self.running = False

    def accept_client(self, client_addr, message):
        try:
            if not message:
                return False
            name = message.split(":")[1]  # Extract the client name
            if name in self.clients.values():
                message = "Name already taken.".encode("utf-8")
                self.server_socket.sendto(message, client_addr)
                return False
            else:
                message = "Welcome".encode("utf-8")
                self.server_socket.sendto(message, client_addr)
                self.clients[client_addr] = name
                welcome_msg = f"User {name} joined"
                self.messages.append((client_addr, welcome_msg))
                self.broadcast()
                return True
        except Exception as e:
            print(f"Error at accept_client(): {e}")

    def close_client(self, client_addr):
        try:
            if client_addr in self.clients:
                client_name = self.clients.pop(client_addr)
                leave_msg = (client_addr, f"User {client_name} left")
                self.messages.append(leave_msg)
                self.broadcast()
                return True
        except Exception as e:
            print(f"Error at close_client(): {e}")
        return False

    def broadcast(self):
        try:
            client_addr, message = self.messages[-1]
            formatted_message = f"{message}".encode("utf-8")

            for i in self.clients:
                if i != client_addr:
                    self.server_socket.sendto(formatted_message, i)

        except Exception as e:
            print(f"Error at broadcast() {e}")

    def shutdown(self):
        try:
            self.run_event.set()
            time.sleep(1)
            print("Shutting down...")
            for i in list(self.clients.keys()):
                shutdown = "server-shutdown".encode("utf-8")
                self.server_socket.sendto(shutdown, i)
                self.close_client(i)
            time.sleep(1)
            print(f"clients:{self.get_clients_number()}")
            self.server_socket.close()
        except Exception as e:
            print(f"Error at shutdown(): {e}")
            self.run_event.set()
            self.server_socket.close()

    def get_clients_number(self):
        return len(self.clients)

    def run(self):
        print(
            f"Launching chatroom server on address: {self.address}:{self.server_port}"
        )
        print("Press CTRL+C to shut down the server.")
        print("Waiting for users to join...")
        while not self.run_event.is_set():
            try:
                # Try to accept a client connection
                if select.select([self.server_socket], [], [], 1)[0]:
                    print(f"num clients: {self.get_clients_number()}")
                    data, client_address = self.server_socket.recvfrom(1024)
                    message = data.decode("utf-8")
                    if message.startswith("join"):
                        self.accept_client(client_address, message)
                    elif message.endswith("exit"):
                        self.close_client(client_address)
                    else:
                        if client_address not in self.clients:
                            print("Error: please join first.")
                        else:
                            self.messages.append((client_address, message))
                            self.broadcast()
            except KeyboardInterrupt:
                break
            except Exception as e:
                break
        self.run_event.set()
        self.shutdown()


class ClientUDP:
    def __init__(self, client_name, server_port):
        print("UDP CHATROOM\nThis is the client side.")
        # Initialize instance variables and threading events
        self.client_name = client_name
        self.prompt = f"{self.client_name}: "
        self.server_addr = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_port = server_port
        self.server_con = (self.server_addr, self.server_port)
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event()

    def connect_server(self):
        try:
            join_message = f"join:{self.client_name}".encode("utf-8")
            self.client_socket.sendto(join_message, self.server_con)
            response, _ = self.client_socket.recvfrom(1024)
            response = response.decode("utf-8")
            if "Welcome" in response:
                return True
            else:
                print("Error: Name already taken.")
                return False
        except Exception as e:
            print(f"Error at connect_server(): {e}")
        return False

    def send(self, text):
        try:
            message = f"{self.client_name}:{text}"
            encoded_message = message.encode("utf-8")
            self.client_socket.sendto(encoded_message, self.server_con)
            return True
        except Exception as e:
            print(f"Error at client send(): {e}")

    def receive(self):
        while not self.exit_receive.is_set():
            try:
                ready = select.select(
                    [self.client_socket], [], [], 1
                )  # 1-second timeout
                if ready[0]:
                    message, _ = self.client_socket.recvfrom(1024)
                    message = message.decode("utf-8")
                    if message == "server-shutdown":
                        self.exit_receive.set()
                        self.exit_run.set()
                        break

                    sys.stdout.write("\r" + " " * (len(self.client_name + ": ")) + "\r")

                    # Print the received message
                    print(f"{message}")

                    # Re-display prompt
                    sys.stdout.write(self.prompt)
                    sys.stdout.flush()
                    readline.redisplay()
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.exit_run.set()
                self.exit_receive.set()
                break
        self.client_socket.close()

    def run(self):
        if self.connect_server():
            receive_thread = threading.Thread(target=self.receive, args=())
            receive_thread.start()
            while not self.exit_run.is_set():
                try:
                    message = input(self.prompt)
                    self.send(message)
                    if message == "exit":
                        break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    break
        self.exit_run.set()
        self.exit_receive.set()
