def saveBinaryAsImage(binary, path):
  with open(path, "wb") as image:
    image.write(binary)