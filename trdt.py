import wifi
import socketpool
import ssl

# Replace with your network credentials
SSID = "NatchoWiFi"
PASSWORD = "SimbaFionaStinkyButt"

print("Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("Connected!")

# Set up the socket pool and requests session
pool = socketpool.SocketPool(wifi.radio)
context = ssl.create_default_context()
