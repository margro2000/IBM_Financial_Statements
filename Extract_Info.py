import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

client = vision.ImageAnnotatorClient()
with io.open('Amazon_10-k_2018-18.png', 'rb') as image_file:
        content = image_file.read()
image = types.Image(content=content)
response = client.document_text_detection(image=image)
document = response.full_text_annotation

def draw_boxes(image, bounds, color,width=5):
    draw = ImageDraw.Draw(image)
    for bound in bounds:
        draw.line([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y,
            bound.vertices[0].x, bound.vertices[0].y],fill=color, width=width)
    return image

bounds = 8;

draw_boxes(image,bounds, 'yellow')

def text_within(document,x1,y1,x2,y2):
	text=""
	for page in document.pages:
		for block in page.blocks:
			for paragraph in block.paragraphs:
				for word in paragraph.words:
					for symbol in word.symbols:
						min_x=min(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
						max_x=max(symbol.bounding_box.vertices[0].x,symbol.bounding_box.vertices[1].x,symbol.bounding_box.vertices[2].x,symbol.bounding_box.vertices[3].x)
						min_y=min(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
						max_y=max(symbol.bounding_box.vertices[0].y,symbol.bounding_box.vertices[1].y,symbol.bounding_box.vertices[2].y,symbol.bounding_box.vertices[3].y)
						if(min_x >= x1 and max_x <= x2 and min_y >= y1 and max_y <= y2):
							text+=symbol.text
						if(symbol.property.detected_break.type==1 or
                			symbol.property.detected_break.type==3):
							text+=' '
						if(symbol.property.detected_break.type==2):
							text+='\t'
						if(symbol.property.detected_break.type==5):
							text+='\n'
			return text

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
                    assembled_word=assemble_word(word)
                    if(assembled_word==word_to_find):
                        return word.bounding_box

location=find_word_location(document,'Overdrafts')

text_within(document, location.vertices[1].x, location.vertices[1].y, 30+location.vertices[1].x+(location.vertices[1].x-location.vertices[0].x),location.vertices[2].y)
