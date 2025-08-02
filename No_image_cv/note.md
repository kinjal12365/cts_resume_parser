To handle cv's which are directly converted from image to pdf we can use ocr technologies
and coming from cs & aiml backgrounds, the team has worked with these technologies as well 


but currently we are not dealing with the pdfs which are directly converted from images as to handle them we need to use

OCR which requires -
easyocr
torch
torchvision
opencv-python
scipy

Installing and packaging all of these will increase the size of zip way above 250mb+

So, its not feasable to apply it and we are keeping this as a conceptual part not implementing it directly
in the project as most of the pdfs uploaded as resume are text based not image based.
