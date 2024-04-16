from enum import IntEnum
import socket
import time 
  
class Protocols(IntEnum):
  NONE = 0
  BIT_ALTERNANTE = 1
  GO_BACK_N = 2
  
class UDPServer:
  
  routes = {}
  END_MESSAGE = b"FIM"
  SEQ_SIZE = 5
  ACK_MESSAGE = b"ACK"
  TIMEOUT = .1
  TIME_BETWEEN_PACKAGES = 0
  WINDOWN_SIZE = 4
  
  def __init__(self, props):
    self.SERVER_IP = props["SERVER_IP"]
    self.SERVER_PORT = props["SERVER_PORT"]
    self.BUFFER_SIZE = props["BUFFER_SIZE"]
    self.PROTOCOL = props["PROTOCOL"]
    self.showLogs = props["SHOW_LOGS"] if "SHOW_LOGS" in props else True
    # Create a datagram socket
    self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
  def listen(self):
    # Bind to address and ip
    self.UDPServerSocket.bind((self.SERVER_IP, self.SERVER_PORT))
    self.__log(f"UDP server up and listening on {self.SERVER_IP}:{self.SERVER_PORT}")
    
    while(True):
      [bytesReceived, address] = self.UDPServerSocket.recvfrom(self.BUFFER_SIZE)
      message = self.__bytesToString(bytesReceived)
      route = self.routes.get(message.upper())
      
      if(route):
        route(message, address)
      else:
        self.send("Route not found", address)
    
  def send(self, message, address):
    bytesMessage = self.__stringToBytes(message) + self.END_MESSAGE
    dataSize = self.BUFFER_SIZE - self.SEQ_SIZE
    packages = [bytesMessage[i:i + dataSize] for i in range(0, len(bytesMessage), dataSize)]
    
    if(self.PROTOCOL == Protocols.BIT_ALTERNANTE):
      self.__protocolBitAlternante(packages, address)
    elif(self.PROTOCOL == Protocols.NONE):
      self.__protocolNone(packages, address)
    elif(self.PROTOCOL == Protocols.GO_BACK_N):
      self.__protocolGoBackN(packages, address)
        
        
  def __protocolGoBackN(self, packages, address):
    # Envia n pacotes por vez, e espera receber n ACKS. Após receber tds os ACS ou dar timeout, move a janela com base no ultimo ACK recebido
    self.__log("\nProtocol: Go Back N")
    
    i = 0
    while i < len(packages):
      # Envia n pacotes em paralelo
      self.__log(f"\nSending packages {i + 1} to {min(i + self.WINDOWN_SIZE, len(packages))} to client")
      j = i
      while j < i + self.WINDOWN_SIZE and j < len(packages):
        package = packages[j]
        seq = j + 1
        self.__log(f"Sending package {seq} to client")
        package = self.__stringToBytes(str(seq).zfill(self.SEQ_SIZE)) + package
        # Sending a reply to client
        self.UDPServerSocket.sendto(package, address)
        j += 1
        
      # Recebe n ACKs
      self.__log(f"Waiting for ACKs {i + 1} to {min(i + self.WINDOWN_SIZE, len(packages))} from client...")
      seqACKSReceived = []
      self.UDPServerSocket.settimeout(self.TIMEOUT)
      for _ in range(self.WINDOWN_SIZE):
        if _ + i >= len(packages):
          break
        try:
          [bytesReceived, address] = self.UDPServerSocket.recvfrom(self.BUFFER_SIZE)
          if(bytesReceived.startswith(self.ACK_MESSAGE)):
            seqReceived = int(self.__bytesToString(bytesReceived[len(self.ACK_MESSAGE):]))
            self.__log(f"Received ACK {seqReceived} from client")
            seqACKSReceived.append(seqReceived)
        except socket.timeout:
          self.__log(f"Timeout for ACK")
      self.UDPServerSocket.settimeout(None)
      
      # Verifica quantos ACKs foram recebidos em sequencia e move a janela
      seqACKSReceived.sort()
      greater = seqACKSReceived[-1] if len(seqACKSReceived) > 0 else 0
      # ACKSReceived = 0
      # for d, _ in enumerate(seqACKSReceived):
      #   last = i if d == 0 else seqACKSReceived[d - 1]
      #   if seqACKSReceived[d] - last != 1:
      #     break
      #   else:
      #     ACKSReceived += 1
      # self.__log("ACKs received in sequence:", seqACKSReceived, ACKSReceived)
          
      self.__log("ACKs received in sequence:", seqACKSReceived, greater)
        
      if i < len(packages) - 1:
        time.sleep(self.TIME_BETWEEN_PACKAGES)
      
      i = min(greater, len(packages))    
    
  def __protocolBitAlternante(self, packages, address):
    # Envia 1 pacote por vez, e espera receber o ACK do cliente para enviar o próximo pacote
    self.__log("\nProtocol: Bit Alternante")
    
    i = 0
    while i < len(packages):
      package = packages[i]
      seq = i + 1
      self.__log(f"\nSending package {seq} to client")
      package = self.__stringToBytes(str(seq).zfill(self.SEQ_SIZE)) + package
      # Sending a reply to client
      self.UDPServerSocket.sendto(package, address)
      
      # Receive ACK from client
      self.__log(f"Waiting for ACK {seq} from client...")
      
      ACKReceived = False
      self.UDPServerSocket.settimeout(self.TIMEOUT)
      try:
        [bytesReceived, address] = self.UDPServerSocket.recvfrom(self.BUFFER_SIZE)
        if(bytesReceived.startswith(self.ACK_MESSAGE)):
          seqReceived = int(self.__bytesToString(bytesReceived[len(self.ACK_MESSAGE):]))
          self.__log(f"Received ACK {seqReceived} from client")
          if(seq == seqReceived):
            ACKReceived = True
      except socket.timeout:
        self.__log(f"Timeout for ACK {seq}")
      self.UDPServerSocket.settimeout(None)
        
      if(ACKReceived == False):
        i -= 1
      
      if i < len(packages) - 1:
        time.sleep(self.TIME_BETWEEN_PACKAGES)
        
      i += 1
        
  def __protocolNone(self, packages, address):
    # Envia cada pacote sem esperar ACK do cliente
    self.__log("\nProtocol: None")
    for i, package in enumerate(packages):
      seq = i + 1
      self.__log(f"\nSending package {seq} to client")
      package = self.__stringToBytes(str(seq).zfill(self.SEQ_SIZE)) + package
      # Sending a reply to client
      self.UDPServerSocket.sendto(package, address)
      if i < len(packages) - 1:
        time.sleep(.5)
    
  def addRoute(self, routeName, callback):
    self.routes[routeName.upper()] = callback
  
  def __stringToBytes(self, string):
    if type(string) == bytes:
      return string
    return str.encode(string)

  def __bytesToString(self, bytes):
    return bytes.decode('utf-8')
  
  def __log(self, *message):
    if(self.showLogs):
      print(*message)