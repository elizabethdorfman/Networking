# Networking Projects

This repository contains a collection of networking-related projects, each focusing on a specific concept or protocol. The projects are organized into separate folders for easy navigation.

## Folder Structure

### 1. **HTTP Server**
   - Implementation of an HTTP server capable of handling GET and POST requests.
   - Features include:
     - Parsing HTTP requests and sending appropriate responses.
     - Handling client sessions.
     - Serving static files and processing dynamic requests.

### 2. **TCP/UDP Chatroom**
   - A chatroom application built using both TCP and UDP protocols.
   - Features include:
     - Broadcasting messages to multiple clients.
     - Reliable message delivery using TCP.
     - Lightweight communication using UDP.

### 3. **Go Back N**
   - Simulation of the Go-Back-N Automatic Repeat Request (ARQ) protocol for reliable data transmission.
   - Features include:
     - Sliding window mechanism.
     - Handling packet loss, retransmissions, and acknowledgments.
     - Logging of events for analysis.

### 4. **Bellman Ford**
   - Implementation of the Bellman-Ford algorithm for finding the shortest paths in a weighted network.
   - Features include:
     - Detection of negative weight cycles.
     - Calculation of shortest paths from a source node to all other nodes.

## Setup

To launch the server for any of the projects and test their functionality:

Clone the repository:
   ```bash
   git clone https://github.com/elizabethdorfman/Networking.git
   cd Networking
   ```

## Testing Each Project

1. **HTTP Server:**
   - Launch the server by running the python file
     ```bash
     python3 server.py
     ```
   - Use a browser to send HTTP GET/POST requests to the server.

2. **TCP/UDP Chatroom:**
   - Open multiple terminal windows.
   - Run the server in one terminal:
     ```bash
     python3 server.py
     ```
   - Connect multiple clients from separate terminals:
     ```bash
     python3 client.py
     ```
   - Send messages from one client and confirm that the other clients receive them.
   - Change from TCP and UDP by modifying the import line to
      ```bash
      from chatroom import ClientTCP
      ```
      
3. **Go Back N:**
   - Run the test file directly to verify the implementation:
     ```bash
     python3 test_gbn.py
     ```
   - The test file will simulate the Go-Back-N protocol, including packet loss and retransmissions, and log the results for verification.

4. **Bellman Ford:**
   - Run the script with a predefined graph or input data.
     ```bash
     python3 bellmanford.py matrix.txt
     ```
   - Verify the output for shortest paths and negative weight cycle detection.

