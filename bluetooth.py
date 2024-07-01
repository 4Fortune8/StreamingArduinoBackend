import time
import struct
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# Function to calculate CRC for a given data array
def calculate_crc(data):
    crc = 0
    for byte in data:
        crc ^= byte
    print(crc)
    return crc

# Custom packet data
custom_packet = [ord('!'), ord('B'), ord('4'), ord('1')]
crc = calculate_crc(custom_packet)

ble = BLERadio()
pos = 1
while True:
    print("Scanning...")
    for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=5):
        if UARTService in advertisement.services:
            print("Found UART service!")
            try:
                peripheral = ble.connect(advertisement)
                uart_service = peripheral[UARTService]
                print("Connected to UART service!")
                while peripheral.connected:
                    # Construct the packet
                    if pos >= 9:
                        pos = 0
                        
                    custom_packet = [ord('!'), ord('B'), ord('4'), ord(str(pos))]
                    crc = calculate_crc(custom_packet)
                    packet_data = custom_packet + [crc]
                    # Pack the packet into bytes
                    packet_bytes = bytes(packet_data)
                    # Send the packet over UART
                    uart_service.write(packet_bytes)
                    print(f"Sent custom packet: {packet_data}")
                    time.sleep(5)
                    pos += 1
                break
            except Exception as e:
                print(f"Connection error: {e}")
    ble.stop_scan()

