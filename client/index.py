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
  "BUFFER_SIZE": 1024 * 4,
  "PROTOCOL": UDPService.Protocols.GO_BACK_N,
  "SHOW_LOGS": True,
  "ERROR_RATE": 5
})

image = clientDriver.request(message=route)
# print(f"\nMessage from Server: '{image}'")

ImageService.saveBinaryAsImage(image, f"./client/images/{route.upper()}_{TimeService.now()}.jpg")