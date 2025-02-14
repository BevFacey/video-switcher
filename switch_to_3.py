import socket
UDP_IP = '192.168.140.25'  # VP-440 IP address (default)
UDP_PORT = 50000         # VP-440 UDP port (default)

destination_input = 3
command = '#ROUTE 12,1,' + str(destination_input-1) + '\r'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
sock.close()