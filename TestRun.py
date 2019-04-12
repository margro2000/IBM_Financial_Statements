import io, os, argparse, re
from enum import Enum
import csv
import json

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
#from wand.image import Image
#from pdf2image import convert_from_path

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
    doc_texts = response.full_text_annotation
    #count = -1
    print('Texts:')

    #Finds word on page and its y vertices and  prints it as well as its y vertices
    try:
        for text in texts:
            if text.description==word:
                #count = count + 1
                #if isTable(response, path, word)[count]:
                print('\n"{}"'.format(text.description))
                vertices1 = ({'({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices})
                print('bounds: {}'.format(','.join(vertices1)))
        vy = [int((tup.split(","))[1][0:-1]) for tup in vertices1]
        vy = sorted(list(dict.fromkeys(vy)))
    except:
        print("Error extracting word \"" + word + "\"")

    #Finds year on page and prints it as well as prints its y vertices
    try:
        for text in texts:
            #this willl capture the most recent instance of the year
            if text.description==year:
                print('\n"{}"'.format(text.description))
                vertices2 = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])
                print('bounds: {}'.format(','.join(vertices2)))
        vx = [int((tup.split(","))[0][1:]) for tup in vertices2]
        vx = sorted(list(dict.fromkeys(vx)))
    except:
        print("Error extracting year \"" + year + "\"")

    try:
        output = ""
        confidence = 0
        print("VX" + str(vx))
        for page in doc_texts.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word_obj in paragraph.words:
                        #assemble word
                        word_text = ''.join([
                            symbol.text for symbol in word_obj.symbols
                        ])
                        mx = set()
                        my = set()
                        for vertex in word_obj.bounding_box.vertices:
                            mx.add(vertex.x)
                            my.add(vertex.y)
                        my = min(my)
                        mx = sorted(mx)
                        if vy[0] == my:
                            print(word_text)
                            print(mx[0])
                            print(mx[1])
                            if mx[0] <= vx[1] and vx[1] <= mx[1]:
                                output = word_text
                                confidence = get_confidence(word_obj)
    except:
        print("Error extracting intersection of word \"" + word + "\" and year \"" + year + "\"")

    #print(output)
    #print(confidence)
    #append_csv(word, year, output, confidence)
    return (output, confidence)

def detect_document(response, path):
    """Detects document features in an image."""

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
    # TODO: fix the fact that all confidences are zero
    for symbol in word.symbols:
        print("symconf: " + str(symbol.confidence))
        if symbol.confidence < confidenceLevel:
            confidenceLevel = symbol.confidence
            print("conflevel: " + str(confidenceLevel))
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
    #word.confidence = confidenceCategory
    #return word.confidence
    return confidenceCategory

def pdfToPng(path, popplerPath):
    pass
    # TODO: implement pdfToPng
    #pages = convert_from_path(path, 500, poppler_path = popplerPath)
    #counter = 1
    #for page in pages:
    #    page.save(path[:-4] + str(counter) + '.png', 'PNG')

    # with(Image(filename=path, resolution=120)) as source: 
    #     images = source.sequence
    #     pages = len(images)
    #     for i in range(pages):
    #         n = i + 1
    #         newfilename = f[:-4] + str(n) + '.png'
    #         Image(images[i]).save(filename=newfilename)

def append_csv(measure, year, value, confidence, company):
    try:
        with open(company + ".csv", "r") as x:
            pass
    except:
        with open(company + ".csv", "wt") as x:
            x.write("Measure,Year,Value,Confidence\n")
    
    with open(company + ".csv", "a") as x:
        x.write(str(measure) + ",")
        x.write(str(year) + ",")
        if "," in value:
            z=value.split(",")
            y= "".join(z)
            x.write(y + ",")
        x.write(str(confidence) + "\n")

if __name__=="__main__":
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    thePath = 'Amazon_10-K_2018'
    word = "income"
    
    current_year = int(thePath.split("_")[2], 10)
    final_year = current_year - 2

    # The name of the image file to annotate
    file_path = os.path.join(
        os.path.dirname(__file__),
        thePath)

    for file_name in os.listdir(file_path):
        theCompany = file_name.split("_")[0]
        with io.open(os.path.join(file_path,file_name), 'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)

        response_doc = client.document_text_detection(image=image)
        response = client.text_detection(image=image)

        cur_year = current_year
        while cur_year >= final_year:
            (output, confidence) = detect_text(response, file_name, word, str(cur_year))
            append_csv(word, cur_year, output, confidence, theCompany)
            cur_year = cur_year - 1
    
    #detect_document(response_doc, file_name)
    #detect_text(response, file_name, "sales", "2018")
    #printAllText(response, file_name)
    #create_labels()
    #print(isTable(response, file_name, "earnings"))
