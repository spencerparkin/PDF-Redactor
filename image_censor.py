# image_censor.py

import os
import pytesseract
import shutil

from PIL import Image, ImageDraw

offending_words_list = [
    # To be clear, I'm not offended by the Lord's name, but I am offended by how it is often used.
    'jesus',
    'christ',
    'goddamn',

    # Why these are offensive should be clear.
    'fuck',
    'shit',
    'damn',
    'bastard',
    'bitch'
]

class Box:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

def process_image(image_path):
    print(f'Processing: {image_path}...')

    # Load the pixel data.
    image = Image.open(image_path)

    # Call the magical image to text function.
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # Grab parallel arrays we want.
    word_list = data['text']
    x_list = data['left']
    y_list = data['top']
    w_list = data['width']
    h_list = data['height']

    # Make a list of redaction boxes.
    box_list = []
    for i in range(len(word_list)):
        word = word_list[i].lower()
        if len(word) == 0:
            continue
        for offending_word in offending_words_list:
            if offending_word in word:
                box = Box(x_list[i], y_list[i], w_list[i], h_list[i])
                box_list.append(box)

    if len(box_list) > 0:
        print(f'Redacting {len(box_list)} word(s)...')

        # Make sure we backup the image file before we modify it.
        path, ext = os.path.splitext(image_path)
        image_backup_path = path + '.backup' + ext
        shutil.copy(image_path, image_backup_path)

        # Block out the offending words.
        draw = ImageDraw.Draw(image)
        for box in box_list:
            draw.rectangle([box.x, box.y, box.x + box.w, box.y + box.h], fill='black')
        
        # Overwrite the image.
        image.save(image_path)
    
    return len(box_list)

def main():
    image_folder = 'C:/Spencer/ebooks/processed'
    redaction_count = 0
    for root, dirs, files in os.walk(image_folder):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext == '.png' or ext == '.jpg':
                redaction_count += process_image(os.path.join(root, file))

    print(f'Total number of redactions: {redaction_count}')

if __name__ == '__main__':
    main()