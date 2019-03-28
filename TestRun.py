import io
import os
import argparse
from enum import Enum
import re

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
#from PIL import Image, ImageDraw

# Instantiates a client

client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
    'Amazon_10-K_2018-18.png')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations
document = response.full_text_annotation

print('Labels:')
for label in labels:
    print(label.description)

#find document type method
print("I am finding doc type!")

#findDocType()

def detect_text(path, word, year):
    """Detects text in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        if text.description==word:
            print('\n"{}"'.format(text.description))
            vertices1 = ({'({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices})
            print('bounds: {}'.format(','.join(vertices1)))
    vy = [int((tup.split(","))[1][0:-1]) for tup in vertices1]
    vy = sorted(list(dict.fromkeys(vy)))


    for text in texts:
        if text.description==year:
            print('\n"{}"'.format(text.description))
            vertices2 = (['({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices])
            print('bounds: {}'.format(','.join(vertices2)))
    vx = [int((tup.split(","))[0][1:]) for tup in vertices2]
    vx = sorted(list(dict.fromkeys(vx)))


    for text in texts:
        maybe = (['({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices])
        my = [(tup.split(","))[1][0:-1] for tup in maybe]
        my = sorted(list(dict.fromkeys(my)))
        mx = [int((tup.split(","))[0][1:]) for tup in maybe]
        mx = sorted(list(dict.fromkeys(mx)))
        if vy[0] == int(my[0]):
            if vx[1] in range(mx[0], mx[1]):
                print(text.description)

def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))

                    for symbol in word.symbols:
                        print(symbol.text)


#detect_document('./Amazon_10-k_2018-18.png')

detect_text('./Amazon_10-k_2018-18.png', "sales", "2014")


def assemble_word(word):
    assembled_word=""
    for symbol in word.symbols:
        assembled_word+=symbol.text
    return assembled_word

def find_word_location(document,word_to_find):
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    assembled_word=assemble_word(word_to_find)
                    if(assembled_word==word_to_find):
                        return word.bounding_box

location=find_word_location(document,"for")
print(location)


def isTable(path, word):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    #everything above this is just the setup for reading in all of the words and polygons

    #this part below checks fot the input word
    mightBeTable = []
    for text in texts:
        if text.description==word:
            #this part checks back through the whole list of all words to find words with the correct dimensions for their bounding boxes.
            yVertexSet = set()
            xVertexSet = set()
            for vertex in text.bounding_poly.vertices:
                yVertexSet.add(vertex.y)
                xVertexSet.add(vertex.x)
            rightVertex = max(xVertexSet)
            topVertex = min(yVertexSet)
            bottomVertex = max(yVertexSet)
            #til this point, it is setting the bounds for the "correct dimensions"
            for word in texts:
                for v in word.bounding_poly.vertices:
                    if (topVertex <= v.y and v.y <= bottomVertex) or (topVertex > v.y and bottomVertex) and v.x > rightVertex: #checks to see if any vertex of the examined word is in line with the original word, as well as being to the right of the original word
                        mightBeTable.append(word)
    #this next part is going to check to see if the words that were in the right place are numbers, thus qualifiying if the word is a row in a table
    numberPercent = 0 #tracks how many of the words are numbers
    totalWords = 0 #tracks how many words we examine
    for word in mightBeTable:
        if re.fullmatch(r'\(?\d+[.,0-9]*\)?', word.description) != None: #might be able to make this regex better if I account for the fact that there would be groups of three digits between commas
            numberPercent += 1
        totalWords += 1
    return numberPercent/totalWords > 0.4




print(isTable('./Amazon_10-k_2018-18.png', "sales"))
#check if table method that returns true or false
#
#method-> extract data
#parameter String-> extraction World
