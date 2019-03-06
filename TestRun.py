import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
<<<<<<< HEAD
    'IMG_3124.JPG')
=======
    'wholesome_pic.png')
>>>>>>> 7bc22369913c81ada3fcc023ad6fea2c2acc540a

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)

#find document type method
def findDocType():
	print("I am finding doc type!")

findDocType()

#check if table method that returns true or false
#
#method-> extract data
#parameter String-> extraction World
