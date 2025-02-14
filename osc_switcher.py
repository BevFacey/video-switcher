#!/usr/bin/env python3

# pip install python-osc
from pythonosc import dispatcher
from pythonosc import osc_server
import socket
import argparse

class KramerVP440:
    def __init__(self, ip='192.168.140.25', port=50000):
        """Initialize the Kramer VP-440 controller.
        
        Args:
            ip (str): IP address of the VP-440
            port (int): UDP port of the VP-440
        """
        self.ip = ip
        self.port = port
        
    def switch_input(self, input_number):
        """Switch to the specified input source.
        
        Args:
            input_number (int): Input number (1-4)
        """
        if not 1 <= input_number <= 6:
            print(f"Invalid input number: {input_number}. Must be between 1 and 6.")
            return
            
        # VP-440 expects zero-based input numbers
        command = f'#ROUTE 12,1,{input_number-1}\r'
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(command.encode(), (self.ip, self.port))
            print(f"Switched to input {input_number}")
        except Exception as e:
            print(f"Error sending command to VP-440: {e}")
        finally:
            sock.close()

def handle_input_change(addr, args, input_number):
    """OSC message handler for input changes.
    
    Args:
        addr: OSC address pattern
        args: Arguments passed from dispatcher
        input_number: Input number received from OSC message
    """
    switcher = args[0]
    try:
        input_num = int(input_number)
        switcher.switch_input(input_num)
    except ValueError:
        print(f"Invalid input number received: {input_number}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Kramer VP-440 OSC Control')
    parser.add_argument('--switcher-ip', default='192.168.140.25', help='IP address of the VP-440')
    parser.add_argument('--switcher-port', type=int, default=50000, help='UDP port of the VP-440')
    parser.add_argument('--osc-ip', default='0.0.0.0', help='IP address to listen for OSC messages')
    parser.add_argument('--osc-port', type=int, default=5005, help='Port to listen for OSC messages')
    args = parser.parse_args()
    
    # Initialize the VP-440 controller
    switcher = KramerVP440(args.switcher_ip, args.switcher_port)
    
    # Set up OSC dispatcher
    dispatch = dispatcher.Dispatcher()
    dispatch.map("/input", handle_input_change, switcher)
    
    # Start OSC server
    server = osc_server.ThreadingOSCUDPServer(
        (args.osc_ip, args.osc_port), dispatch)
    
    print(f"Serving on {server.server_address}")
    print("Send OSC message to /input with an integer argument (1-6) to switch inputs")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")