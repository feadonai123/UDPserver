def readImageAsBinary(path):
  with open(path, "rb") as image:
    return image.read()
  
def saveBinaryAsImage(binary, path):
  with open(path, "wb") as image:
    image.write(binary)