import bluetooth
import subprocess
import binascii
import time
import os
from obd_generator import *

SCANNER_TIME = 3

# NOTE: shuold be run as root

def main():
	
	try:
		# switch off subprocesses output
		devs = open(os.devnull,"w")
		
		# make directory with root privileges to store pcap output file
		# tshark output can be stored only in root's directories
		subprocess.call("mkdir ./capture",shell=True,stdout=devs,stderr=devs)
		
		#run tshark with root privileges on bluetooth interface
		thread=subprocess.Popen(["tshark", "-w", "./capture/capture.pcap", "-i", "bluetooth0"],stdout=devs,stderr=devs)
		
		#STEP 1: BLUETOOTH SCANNER
		devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = SCANNER_TIME)

		if len(devices) == 0:
			print ("No devices found")
			thread.terminate()
			quit()

		i=0
		dev_names = []
		dev_addr = []
		
		# print services for each discovered device
		for addr, name in devices:
			#device_name = bluetooth.lookup_name(addr)
			dev_addr.append(addr)
			dev_names.append(name)
			print "Device N." + str(i) + ": " + addr + ": " + name		
			
			for services in bluetooth.find_service(address = addr):
				print "   Name: ", services["name"]
				print "   Description: ", services["description"]
				print "   Protocol: ", services["protocol"]
				print "   Provider: ", services["provider"]
				print "   Port: ", services["port"]
				print "   Service id: ", services["service-id"]
				print ""
			i=i+1	
		
		
		#STEP 2: DEVICE CHOOSING
		try:
			userInput=(raw_input('Chose a device number for pairing (q for quit):'))
			if userInput == 'q':
				thread.terminate()
				quit()
			deviceNum = int(userInput)
		except ValueError:
			print "Not a number"
			thread.terminate()
			quit()
		if deviceNum >= len(devices):
			print "Input error: no such device"
			thread.terminate()
			quit()

		address = dev_addr[deviceNum]
		name = dev_names[deviceNum]
		print "You have chosen device " + str(deviceNum) + ": " + address + "(" + name + ")"
		
		#STEP 3: PAIRING
		try:
			port = int(raw_input('Chose the port :'))         # RFCOMM port
		except ValueError:
			print "Not a number"
			thread.terminate()
			quit()
			
		try:
			# bluetooth protocol: RFCOMM
			socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			socket.connect((address,port))
			print "Device connected"
			
			# the first packet is equal to the first sent by the official Andoid application for OBDII interaction
			socket.send("ATZ\r")
			print "Sent: ATZ\r"
			# expected answer is "ELM327 v1.5\r\r"
			
			while True:
				# send pseudo-random generated data
				data = generator()
				socket.send(data)
				print "Sent: ", data
				time.sleep(1)
				
			'''
				#To receive data
				received = socket.recv(1024) # Buffer size
				print "received: ", received
			'''
		
		except bluetooth.btcommon.BluetoothError as err:
			print err
			socket.close()
			
	except KeyboardInterrupt:
		# to intercept CRTL+C interrupt 
		thread.terminate()
		print "\nQuitting..."
	

if __name__ == "__main__":
	main()




	



	
