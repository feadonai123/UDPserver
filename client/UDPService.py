from enum import IntEnum
import random
import socket

class Protocols(IntEnum):
  NONE = 0
  BIT_ALTERNANTE = 1
  GO_BACK_N = 2
  
class UDPClient:
  END_MESSAGE = b"FIM"
  SEQ_SIZE = 5
  ACK_MESSAGE = b"ACK"
  
  def __init__(self, props):
    self.SERVER_IP = props["SERVER_IP"]
    self.SERVER_PORT = props["SERVER_PORT"]
    self.BUFFER_SIZE = props["BUFFER_SIZE"]
    self.PROTOCOL = props["PROTOCOL"]
    self.ERROR_RATE = props["ERROR_RATE"] if "ERROR_RATE" in props else 0
    self.showLogs = props["SHOW_LOGS"] if "SHOW_LOGS" in props else True
    # Create a UDP socket at client side
    self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  
  def request(self, message):
    self.__send(message)
    
    if(self.PROTOCOL == Protocols.BIT_ALTERNANTE):
      result = self.protocolBitAlternante()
    elif(self.PROTOCOL == Protocols.NONE):
      result = self.protocolNone()
    elif(self.PROTOCOL == Protocols.GO_BACK_N):
      result = self.protocolGoBackN()
      
    if result == b"Route not found":
      raise Exception("Route not found")
      
    return result
  
  def protocolGoBackN(self):
    self.__log("\nProtocol: Go Back N")
    
    packages = []
    hasFinished = False
    lastSeqReceived = None
    while hasFinished == False:
      [bytesReceived, address] = self.UDPClientSocket.recvfrom(self.BUFFER_SIZE)
      seqReceived = bytesReceived[:self.SEQ_SIZE]
      hasFinished = bytesReceived.endswith(self.END_MESSAGE)
      dataReceived = bytesReceived[self.SEQ_SIZE:-len(self.END_MESSAGE)] if hasFinished else bytesReceived[self.SEQ_SIZE:]
      
      seqNumber = int(self.__bytesToString(seqReceived))
      self.__log(f"\nReceived from server SEQ {seqNumber}. Tam packages: {len(packages)}")
      
      if seqNumber == len(packages) + 1:
        packages.append(dataReceived)
        lastSeqReceived = seqReceived
        self.__sendACK(seqReceived, address)
      else:
        # Ignore package
        self.__log(f"Package {seqNumber} ignored")
        # send ACK to server
        self.__sendACK(lastSeqReceived, address)
      
    binaryResponse = b"".join(packages)
    return binaryResponse # self.__bytesToString(binaryResponse)
    
  def protocolBitAlternante(self):
    self.__log("\nProtocol: Bit Alternante")
    
    packages = []
    
    hasFinished = False
    while hasFinished == False:
      [bytesReceived, address] = self.UDPClientSocket.recvfrom(self.BUFFER_SIZE)
      
      seqReceived = bytesReceived[:self.SEQ_SIZE]
      hasFinished = bytesReceived.endswith(self.END_MESSAGE)
      dataReceived = bytesReceived[self.SEQ_SIZE:-len(self.END_MESSAGE)] if hasFinished else bytesReceived[self.SEQ_SIZE:]
      
      seqNumber = int(self.__bytesToString(seqReceived))
      self.__log(f"\nReceived from server SEQ {seqNumber}")
      
      if seqNumber == len(packages) + 1:
        packages.append(dataReceived)
        self.__sendACK(seqReceived, address)
      else:
        self.__log(f"Package {seqNumber} already received")
        # send ACK to server
        self.__sendACK(seqReceived, address)
      
    binaryResponse = b"".join(packages)
    return binaryResponse # self.__bytesToString(binaryResponse)
  
  def protocolNone(self):
    self.__log("\nProtocol: None")
    binaryResponse = b""
    hasFinished = False
    while hasFinished == False:
      [bytesReceived, address] = self.UDPClientSocket.recvfrom(self.BUFFER_SIZE)
      self.__log(f"\nReceived from server: {bytesReceived}")
      
      seqReceived = bytesReceived[:self.SEQ_SIZE]
      hasFinished = bytesReceived.endswith(self.END_MESSAGE)
      dataReceived = bytesReceived[self.SEQ_SIZE:-len(self.END_MESSAGE)] if hasFinished else bytesReceived[self.SEQ_SIZE:]
      
      binaryResponse += dataReceived
      
    return binaryResponse # self.__bytesToString(binaryResponse)
  
  def __sendACK(self, seqReceived, address):
    if random.randint(1, 100) > self.ERROR_RATE:
      ack = self.ACK_MESSAGE + seqReceived
      self.UDPClientSocket.sendto(ack, address)
      self.__log(f"Sending ACK to server: {ack}")
    else:
      self.__log(f"ACK {seqReceived} lost")
    
  def __send(self, message):
     # Send to server using created UDP socket
    self.UDPClientSocket.sendto(self.__stringToBytes(message), (self.SERVER_IP, self.SERVER_PORT))
  
  def __stringToBytes(self, string):
    return str.encode(string)

  def __bytesToString(self, bytes):
    return bytes.decode('utf-8')
  
  def __log(self, *message):
    if(self.showLogs):
      print(*message)