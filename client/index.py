import sys
import UDPService
import ImageService
import TimeService

if len(sys.argv) < 2:
  print("Usage: python client.py <route>")
  sys.exit(1)

route = sys.argv[1]

clientDriver = UDPService.UDPClient({
  "SERVER_IP": "127.0.0.1",
  "SERVER_PORT": 1234,
  "BUFFER_SIZE": 1500 * 4,
  "PROTOCOL": UDPService.Protocols.GO_BACK_N,
  "SHOW_LOGS": True,
  "ERROR_RATE_SEND_ACK": 5
})

try:
  image = clientDriver.request(message=route)
  ImageService.saveBinaryAsImage(image, f"./client/images/{route.upper()}_{TimeService.now()}.jpg")
except Exception as e:
  print(f"\nError from Server: '{e}'")
