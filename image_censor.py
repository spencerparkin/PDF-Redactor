# image_censor.py

import os
import pytesseract
import shutil
import fitz
import glob

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

def process_image(image_path, make_backup):
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
        if make_backup:
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

def redact_images_in_folder(image_folder):
    print('Processing folder: ' + image_folder)
    redaction_count = 0
    for root, dirs, files in os.walk(image_folder):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext == '.png' or ext == '.jpg':
                redaction_count += process_image(os.path.join(root, file), make_backup=False)
    print(f'Total number of redactions: {redaction_count}')

def pdf_to_pngs(pdf_path, png_folder):
    pdf = fitz.open(pdf_path)
    for i in range(len(pdf)):
        page = pdf[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        page_path = os.path.join(png_folder, f'page_{i:04d}.png')
        print(f'Writing: {page_path}...')
        pix.save(page_path)
    pdf.close()

def pdf_from_pngs(pdf_path, png_folder, delete_pngs):
    png_file_list = sorted(glob.glob(os.path.join(png_folder, 'page_*.png')))
    image_list = []
    for png_file in png_file_list:
        print(f'Processing: {png_file}...')
        image = Image.open(png_file)
        image = image.convert('RGB')
        image_list.append(image)
    print(f'Writing PDF {pdf_path}...')
    image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
    if delete_pngs:
        for png_file in png_file_list:
            print(f'Deleting {png_file}...')
            os.remove(png_file)

def main():
    source_pdf_path = 'C:/Spencer/ebooks/TheAndromedaStrain.pdf'

    # Dump the PDF to a bunch of PNG files, one per page.
    temp_folder = os.path.join(os.path.split(source_pdf_path)[0], 'temp')
    os.makedirs(temp_folder, exist_ok=False)
    pdf_to_pngs(source_pdf_path, temp_folder)

    # Now go redact the PNG files in the temp folder.
    redact_images_in_folder(temp_folder)

    # Lastly, combine the PNGs back into a PDF.
    destination_pdf_path = os.path.splitext(source_pdf_path)[0] + '_redacted.pdf'
    pdf_from_pngs(destination_pdf_path, temp_folder, delete_pngs=True)
    os.removedirs(temp_folder)

    print('Done!')

if __name__ == '__main__':
    main()