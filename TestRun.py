import io, os, argparse, re
from enum import Enum
import csv
import re

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

def create_labels():
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)

    #Performs label detection on the image file
    response_label = client.label_detection(image=image)
    labels = response_label.label_annotations
    document = response_label.full_text_annotation
    print('Labels:')
    for label in labels:
        print(label.description)


def printAllText(response, path):
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
    # [END vision_python_migration_text_detection]
# [END vision_text_detection]



# Finds input word and input year on page, finds each x and y-values for inputs, and extracts number at the intersection of x y values
def detect_text(response, path, word, year):
    """Detects text in the file."""

    texts = response.text_annotations
    print('Texts:')

    #Finds word on page and its y vertices and  prints it as well as its y vertices
    #try:
    for text in texts:
        if text.description==word:
            print('\n"{}"'.format(text.description))
            vertices1 = ({'({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices})
            print('bounds: {}'.format(','.join(vertices1)))
    vy = [int((tup.split(","))[1][0:-1]) for tup in vertices1]
    vy = sorted(list(dict.fromkeys(vy)))

   # except:
        #print("Error extracting word")

    #try:
        #finds year on page and prints it as well as prints its y vertices
    for text in texts:
        if text.description==year:
            print('\n"{}"'.format(text.description))
            vertices2 = ({'({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices})
            print('bounds: {}'.format(','.join(vertices2)))
    vx = [int((tup.split(","))[0][1:]) for tup in vertices2]
    vx = sorted(list(dict.fromkeys(vx)))

    # except:
    #     print("Error extracting year")

    #find match between x and y vertices and print output
    try:
        for text in texts:
            maybe = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])
            my = [int((tup.split(","))[0][1:]) for tup in maybe]
            my = sorted(list(dict.fromkeys(my)))
            mx = [int((tup.split(","))[0][1:]) for tup in maybe]
            mx = sorted(list(dict.fromkeys(mx)))
            if vy[0] in range(my[0], my[1]) or vy[1] in range(my[0], my[1]):
                if vx[1] in range(mx[0], mx[1]) or vx[0] in range(mx[0], mx[1]):
                    output = text.description
                    test=re.search(r"[0-9]{3},[0-9]{3}", output)
                    if not test:
                        test1=re.search(r"[0-9]{2},[0-9]{3}", output)
                        if not test1:
                            test2=re.search(r"[0-9]{1},[0-9]{3}")
                            print(test2.group())
                            return test2.group()
                        else:
                            print(test1.group())
                            return test1.group()
                    else:
                        print(test.group())
                        return test.group()


    except:
        print("Couldn't find intersection")

# Checks all instaces of 'word' on single page and returns and array of True/False based on if they are in a table or not
def isTable(response, path, word):
    texts = response.text_annotations

    #this part below checks for the input word
    truthArray = []
    for text in texts:
        mightBeTable = []
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
            for word1 in texts:
                y2VertexSet = set()
                x2VertexSet = set()
                for vertex in word1.bounding_poly.vertices:
                    y2VertexSet.add(vertex.y)
                    x2VertexSet.add(vertex.x)
                right2Vertex = max(x2VertexSet)
                top2Vertex = min(y2VertexSet)
                bottom2Vertex = max(y2VertexSet)
                if right2Vertex > rightVertex and ((topVertex <= top2Vertex and top2Vertex < bottomVertex) or (bottomVertex >= bottom2Vertex and bottom2Vertex >= topVertex)  or ((topVertex >= top2Vertex) and (bottomVertex <= bottom2Vertex))): #checks to see if any vertex of the examined word is in line with the original word, as well as being to the right of the original word
                    mightBeTable.append(word1)

            #this next part is going to check to see if the words that were in the right place are numbers, thus qualifiying if the word is a row in a table
            numberPercent = 0 #tracks how many of the words are numbers
            totalWords = 0 #tracks how many words we examine
            for word2 in mightBeTable:

                if re.fullmatch(r'\(?\d+[.,0-9]*\)?', word2.description) != None: #might be able to make this regex better if I account for the fact that there would be groups of three digits between commas
                    numberPercent += 1
                totalWords += 1
            truthArray.append(numberPercent/totalWords > 0.4)
    return truthArray

#checks OCR cnfidence for each character/digit in extracted number and chooses lowest one for overall confidence.
def get_confidence(word):
    confidenceLevel = 1
    confidenceCategory = 0
    for symbol in word.symbols:
        if symbol.confidence < confidenceLevel:
            confidenceLevel = symbol.confidence
    if confidenceLevel > .90:
        confidenceCategory = 10
    elif confidenceLevel > .80:
        confidenceCategory = 9
    elif confidenceLevel > .70:
        confidenceCategory = 8
    elif confidenceLevel > .60:
        confidenceCategory = 7
    elif confidenceLevel > .50:
        confidenceCategory = 6
    elif confidenceLevel > .40:
        confidenceCategory = 5
    elif confidenceLevel > .30:
        confidenceCategory = 4
    elif confidenceLevel > .20:
        confidenceCategory = 3
    elif confidenceLevel > .10:
        confidenceCategory = 2
    else:
        confidenceCategory = 1
    word.confidence = confidenceCategory
    return word.confidence

def append_csv(measure, year, value):
        try:
            with open("newfile2.csv", "rt") as w:
                with open("newfile2.csv", "a") as x:
                    x.write(measure + ",")
                    x.write(str(year) + ",")
                    if value:
                        if "," in value:
                            z=value.split(",")
                            y= "".join(z)
                            x.write(y + "\n")
                    else:
                        x.write("\n")
                        print("append_csv: None Type value passed in...")
        except:
            with open("newfile2.csv", "wt") as x:
                print("dzkjbzknb")
                x.write("Measure,Year,Value,Confidence\n")
                x.write(measure + ",")
                x.write(str(year) + ",")
                if value:
                    if "," in value:
                        z=value.split(",")
                        y= "".join(z)
                        x.write(y + "\n")
                else:
                    x.write("\n")
                    print("append_csv: None Type value passed in...")


def pdfToPng(path):
    # pages = convert_from_path(path, 500)
    # counter = 1
    # for page in pages:
    #     page.save(path[:-4] + str(counter) + '.png', 'PNG')

    with(Image(filename=path, resolution=120)) as source:
        images = source.sequence
        pages = len(images)
        for i in range(pages):
            n = i + 1
            newfilename = f[:-4] + str(n) + '.png'
            Image(images[i]).save(filename=newfilename)

def imgToCSV(client, path):
    detect_text



if __name__=="__main__":


    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    theFile = 'Amazon_10-K_2018-18.png'
    #theFile = pdfToPng("Alphabet_10K_2017.pdf")

    current_year = theFile.split("-")[1][2:]

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        theFile)

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)

    response_doc = client.document_text_detection(image=image)
    response = client.text_detection(image=image)

    word = "income"
    current_year = theFile.split("-")[1][2:]


    #detect_document(response_doc, file_name)

    current_year = int(current_year,10)
    final_year = current_year - 4
    while current_year >= final_year:
        output = detect_text(response, file_name, word, str(current_year))
        append_csv(word, current_year, output)
        current_year = current_year - 1

    #printAllText(response, file_name)

    #create_labels()



    # print(isTable(response, file_name, "earnings"))
