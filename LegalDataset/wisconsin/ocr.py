
import os
import io
from PIL import Image as pImg 
import pytesseract
from wand.image import Image as wandImg 
import gc

#pdf_path = './page3.pdf'

#pdf = wandImg(filename=pdf_path,resolution=300)
#pdfImg=pdf.convert('jpeg')

imgBlobs=[]
extracted_text=[]

def get_text_from_image(pdf_path):
    pdf = wandImg(filename=pdf_path,resolution=300)
    pdf_JPEG = pdf.convert('jpeg')
    imgBlobs = []
    extracted_text = []

    if True:
        n = 1 # skip first page
    else:
        n = 0

    for img in pdf_JPEG.sequence[n:]:
        page = wandImg(image=img)
        imgBlobs.append(page.make_blob('jpeg'))

    #print(len(imgBlobs))
    for imgBlob in imgBlobs:
        print('hi')
        img = pImg.open(io.BytesIO(imgBlob))
        text=pytesseract.image_to_string(img,lang='eng')
        extracted_text.append(text)

    print(extracted_text[2])
    return (extracted_text)

get_text_from_image("../nogit_data/incorrect_text_annot.pdf")
