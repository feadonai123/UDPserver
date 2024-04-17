import UDPService
import ImageService

PATH_IMAGE_SMALL = './server/images/small.jpg'
PATH_IMAGE_BIG = './server/images/big.jpg'

def onTeste(message, address):
  print("\nRoute: TESTE")
  print(f"Client IP Address: '{address}'")
  print(f"Message from Client: '{message}'")
  
  package = "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100"
  serverDriver.send(message=package, address=address)
  
def onSmall(message, address):
  print("\nRoute: SMALL")
  print(f"Client IP Address: '{address}'")
  print(f"Message from Client: '{message}'")
  
  image = ImageService.readImageAsBinary(PATH_IMAGE_SMALL)
  serverDriver.send(message=image, address=address)
  
def onBig(message, address):
  print("\nRoute: BIG")
  print(f"Client IP Address: '{address}'")
  print(f"Message from Client: '{message}'")
  
  image = ImageService.readImageAsBinary(PATH_IMAGE_BIG)
  serverDriver.send(message=image, address=address)

serverDriver = UDPService.UDPServer({
  "SERVER_IP": "127.0.0.1",
  "SERVER_PORT": 1234,
  "BUFFER_SIZE": 1500,
  "PROTOCOL": UDPService.Protocols.GO_BACK_N,
  "SHOW_LOGS": True,
  "ERROR_RATE_CHECKSUM": 5
})

serverDriver.addRoute("TESTE", onTeste)
serverDriver.addRoute("SMALL", onSmall)
serverDriver.addRoute("BIG", onBig)

serverDriver.listen()