#Elizabeth Dorfman
#Test for go back n simulation
#Simulates the Go-Back-N protocol, including packet loss and retransmissions, and logs the results for verification.

from go_back_n import GBN_sender, GBN_receiver
import threading, queue, logging, time

log_file = 'simulation.log'
in_file = 'input_test.txt'
out_file = 'output_test.txt'
with open(in_file, 'w') as f: f.write("Hello World")

window_size = 4
packet_len = 32
nth_packet = 4
timeout_interval = 1

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, 'w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(file_handler)

def monitor_log_file(log_file_path):
    """Continuously monitors the log file for new entries and prints them."""
    with open(log_file_path, 'r') as log_file:
        # Move the cursor to the end of the file to start reading new lines
        log_file.seek(0, 2)
        while True:
            line = log_file.readline()
            if line:
                print(line, end='')  # Print each new log entry as it's written
            else:
                time.sleep(0.1)  # Wait briefly before checking for new entries

# Path to your log file
log_file_path = 'simulation.log'

# Start the log monitoring in a separate thread
log_thread = threading.Thread(target=monitor_log_file, args=(log_file_path,))
log_thread.daemon = True  # Set daemon to allow the program to exit even if this thread is running
log_thread.start()


send_queue, ack_queue = queue.Queue(), queue.Queue()
sender = GBN_sender(input_file = in_file, window_size = window_size, packet_len = packet_len, nth_packet = nth_packet, send_queue = send_queue, ack_queue = ack_queue, timeout_interval = timeout_interval, logger = logger)
receiver = GBN_receiver(output_file = out_file, send_queue = send_queue, ack_queue = ack_queue, logger = logger)

sender_thread = threading.Thread(target=sender.run)
sender_thread.start()
receiver.run()
sender_thread.join()

with open(in_file, 'r') as f1, open(out_file, 'r') as f2: sent, received = f1.read(), f2.read()
if sent == received: print("Data transmitted successfully!")
