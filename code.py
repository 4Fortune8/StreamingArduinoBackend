import wifi
import socketpool
import ssl
import adafruit_requests

# Replace with your network credentials
SSID = "your_SSID"
PASSWORD = "your_PASSWORD"

print("Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("Connected!")

# Set up the socket pool and requests session
pool = socketpool.SocketPool(wifi.radio)
context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, context)
