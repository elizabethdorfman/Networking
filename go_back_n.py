#implement a gobackn protocol based system
#CS 3357, Author: Elizabeth Dorfman, Submitted to: Zubair Fadlullahl, Nov 9, 2025

#Make sure to log all events like the example
#Use timeouts on blocking calls
#Use try, except blocks in methods

import time, threading, queue, logging, select

class GBN_sender:
	def __init__(self, input_file, window_size, packet_len, nth_packet, send_queue, ack_queue, timeout_interval, logger):
		try:
			#Assign inputs to instance variables
			self.input_file = input_file
			self.window_size = window_size
			self.packet_len = packet_len
			self.nth_packet = nth_packet
			self.send_queue = send_queue
			self.ack_queue = ack_queue
			self.timeout_interval = timeout_interval
			self.logger = logger

			#Base of sliding window/ sequence # of first unacknowledged packet
			self.base = 0
			#List of all created packets
			self.packets = self.prepare_packets()
			#A list that tracks which packets have been acknowledged. Initialized to a list of False values with the same length as the packets list.
			self.acks_list = [False for i in range(len(self.packets))]
			#A list that keeps track of the timeout for each packet. Initialized to a list of 0 values with the same length as the packets list.
			self.packet_timers = [0 for i in range(len(self.packets))]
			#A list to track which packets have already been dropped (if using simulated packet loss). Initialized to an empty list.
			self.dropped_list = []
		except Exception as e:
			print(f"Error in GBN sender initialization: {e}.")

	def prepare_packets(self):
		try:
			file = open(self.input_file, 'r')
			text = file.read()
			binary_text = ''.join(format(ord(char), '08b') for char in text)
			num_data_in_packet = self.packet_len - 16
			first = 0
			last = num_data_in_packet
			sequence_num = 0
			packets = []
			while first < len(binary_text):
				sequence_bin = format(sequence_num, '016b')
				data_bin = binary_text[first : last]
				packets.append(data_bin + sequence_bin)
				sequence_num += 1
				last += num_data_in_packet
				first += num_data_in_packet
				if last > len(binary_text):
					last = len(binary_text)

			print(f"packets number:{len(packets)}")
			return packets
		except Exception as e:
			print(f"Error in GBN sender prepare packets: {e}.")
		finally:
			file.close()

	def send_packets(self):
		try:
			i = self.base

			while i < min(self.base + self.window_size, len(self.packets)):
				self.logger.info(f"sending packet {i}")
				if i != 0 and (i+1) % self.nth_packet == 0 and i not in self.dropped_list:
					self.dropped_list.append(i)
					self.logger.info(f"packet {i} dropped")
				else:
					self.send_queue.put(self.packets[i])
				self.packet_timers[i] = time.time()
				i += 1
			#starts from the base and sends packets in sliding window

			#logs an informational message for each packet will be sent, using the logger object

			#Send
			#Start timer for each packet
			#Enqueue packet in send queue

			#if the packet is nth then it is not enqueued and appended to dropped_list array
			#Log dropped packet
		except Exception as e:
			print(f"Error in GBN sender send packets: {e}.")

	def send_next_packet(self):
		try:
			#called from receive_acks
			#increments the base
			#sends last one from window
			self.base += 1
			i = self.base + self.window_size -1
			if i < len(self.packets):
				if i != 0 and (i+1) % self.nth_packet == 0 and i not in self.dropped_list:
					print(self.dropped_list)
					self.dropped_list.append(i)
					self.logger.info(f"packet {i} dropped")
				else:
					self.send_queue.put(self.packets[i])
					self.logger.info(f"sending packet {i}")
				self.packet_timers[i] = time.time()

		except Exception as e:
				print(f"Error in GBN_sender send next packet: {e}.")

	def check_timers(self):
		try:
			#called from run
			#checks if packets have exceeeded timeout time
			#logs a message indicating packet has timed out
			current_time = time.time()
			for i in range(self.base, min(self.base + self.window_size, len(self.packets))):
				if (current_time - self.packet_timers[i]) > self.timeout_interval:
					self.logger.info(f"packet {i} timed out")
					return True
			return False
		except Exception as e:
			print(f"Error in GBN_sender check timers: {e}.")

	def receive_acks(self):
		try:
			#Listens for acknowledgements
			while True:
				try:
					ack = self.ack_queue.get(timeout=0.1)
					ack = int(ack)

					#Check if the ack is the right one
					#If it is we change the ack_list, log file and send next packet
					if self.base == ack and not self.acks_list[ack]:
						self.acks_list[ack] = True
						self.logger.info(f"ack {ack} received")
						self.send_next_packet() #This increments base
					else:
						self.logger.info(f"ack {ack} received, Ignoring")

					#Exit loop once last ack recorded
					if self.acks_list[len(self.packets)-1]:
						return
				except queue.Empty:
					continue
		except Exception as e:
				print(f"Error in GBN_sender receive acks: {e}.")

	def run(self):
		try:
			#Begins by calling send_packets() to transmit the packets in the sliding window
			#Starts a thread to receive acknowledgements
			#Loop- While the base has not reached the total number of packets
   			#It continuously checks for timeouts using check_timers()
			#If a timeout occurs it retransmits the packets in the sliding window
			#At the end when all pafckets have been sent exit while loop
			#Enqueue a none to the send_queue to notify the receiver finished
			self.send_packets()
			ack_rec = threading.Thread(target = self.receive_acks)
			ack_rec.start()
			while self.base < len(self.packets):  # Continue until all packets are acknowledged
				if self.check_timers():
					self.send_packets()  # Retransmit all packets within the current window
				time.sleep(0.5)

			self.send_queue.put(None)
			ack_rec.join()
		except Exception as e:
      			print(f"Error in GBN_sender run: {e}.")

class GBN_receiver:
	def __init__(self, output_file, send_queue, ack_queue, logger):
		try:
			#Assign parameters to instance variables
			self.output_file = output_file
			self.send_queue = send_queue
			self.ack_queue = ack_queue
			self.logger = logger
			#list to store received packets
			self.packet_list = []
			#Stores expected sequeunce num
			self.expected_seq_num = 0

		except Exception as e:
			print(f"Error in GBM receiver initialization: {e}.")

	def process_packet(self, packet):
		try:
			time.sleep(0.001)
			sequence_num = int(packet[-16:], 2)
			data = packet[:-16]
			if self.expected_seq_num == sequence_num:
				self.packet_list.append(data)
				self.ack_queue.put(sequence_num)
				self.logger.info(f"packet {sequence_num} received")
				self.expected_seq_num += 1
				return True
			else:
				self.ack_queue.put(self.expected_seq_num - 1)
				self.logger.info(f"packet {sequence_num} received out of order")
				return False

			#Called from run
			#Checks sequence num and sends acknowledgment accordingly
			#Logs message that packet has been received with logger
		except Exception as e:
			print(f"Error in GBM receiver process packets: {e}.")

	def write_to_file(self):
		try:
			#Called from run
			#extracts data from packets and writes to file
			binary_data = ''.join(self.packet_list)
			text_data = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
			f = open(self.output_file, 'w')
			f.write(text_data)
			self.logger.info(f"Data successfully written to {self.output_file}")
		except Exception as e:
			print(f"Error in GBM receiver write to file: {e}.")
		finally:
			if f:
				f.close()

	def run(self):
		try:
			#Continuously listens for packets from the send queue until None packet
			#Each received packet is processed by calling process_packet()
			#Once all packets have been received, the data is written to the output file using write_to_file()
			while True:
				try:
					packet = self.send_queue.get(timeout=0.1)
					if packet is None:
						break
					else:
						self.process_packet(packet)
				except queue.Empty:
					continue
			self.write_to_file()
		except Exception as e:
      			print(f"Error in GBN receiver run: {e}.")