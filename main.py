from PIL import Image
import matplotlib.pyplot as plt
import re
import os
import shutil
from paddleocr import PaddleOCR, draw_ocr
import argparse

ocr = None
show_image_flag = False

def menu():
    print('\n\nImage Labeler\n  1. Process a file\n  2. Process a folder\n  3. Exit\n')
    choice = input('Enter your choice: ')
    if int(choice) == 1:
        image_name = input('Enter file name: ')
        text = process_single_file(image_name)
    elif int(choice) == 2:
        folder_name = input('Enter folder name: ')
        process_images_in_folder(folder_name)
    elif int(choice) == 3:
        exit()

def process_single_file(image_name):
    load_model()
    try:
        text, result = extract_text(image_name)
        save_image(image_name, text)
        return text, result
    except Exception as e:
        print(f'An error occured: {e}')
        exit()
        # menu()

def process_images_in_folder(folder_name):
    # get all files in folder
    files = os.listdir(folder_name)
    # loop through files
    supported_files = ['.jpg', '.png', '.jpeg', '.webp', '.heic']
    for file in files:
        # check if file is an image
        if file.endswith(tuple(supported_files)):
            # process file
            image_name = os.path.join(folder_name, file)
            text, _ = process_single_file(image_name)
            save_image(image_name, text)

def extract_text(img_path):
    print('----------------------------\nImage: ' + img_path)
    result = ocr.ocr(img_path, cls=True)
    if show_image_flag == True:
        show_image(img_path, result)
    # Extract text values
    text_list = [line[1][0] for box in result for line in box] # bozes > 2 lines
    # Join texts into a single string
    text = ' '.join(text_list)
    print('Recognized text: ' + text)
    # confidence
    confidence_list = [line[1][1] for box in result for line in box]
    confidence = round(sum(confidence_list) / len(confidence_list), 3)
    print('Confidence: ' + str(confidence))
    # Clean text
    pattern = r'[^a-zA-Z0-9\s]'  # Regular expression pattern to match non-alphanumeric characters
    cleaned_text = re.sub(pattern, '', text)
    text = re.sub(r'\s+', ' ', text) # replace multiple spaces with one
    if len(cleaned_text) > 200:
        cleaned_text = cleaned_text[:200]
    print('Cleaned text: ' + cleaned_text)
    return cleaned_text, result

def save_image(image_name, text):
    print('\n\n'+text+'\n\n')
    #text = text.replace(' ', '_') # replace spaces with underscores
    try:
        new_image = text + os.path.splitext(image_name)[1] # new file name with extension
        print('File name: ' + new_image)
        directory = os.path.dirname(image_name) # get directory
        output_directory = os.path.join(directory, 'output') # create output directory
        os.makedirs(output_directory, exist_ok=True) # create directory if it doesn't exist
        new_file_path = os.path.join(output_directory, new_image) # create new file path
        shutil.copy2(image_name, new_file_path) # copy file to new path
    except Exception as e:
        print(f'An error occured: {e}')
        exit()
        #menu()

def load_model():
    global ocr
    if ocr is None:
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) # need to run only once to download and load model into memory
        print('Model loaded')

def show_image(img_path, result):
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='Roboto-Regular.ttf')
    im_show = Image.fromarray(im_show)
    # im_show.save('result.jpg')
    plt.imshow(im_show)
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Labeler')
    parser.add_argument('--dir', help='Folder name to process')
    parser.add_argument('--file', help='File name to process')
    args = parser.parse_args()

    if args.dir:
        process_images_in_folder(args.dir)
    elif args.file:
        process_single_file(args.file)
    else:
        menu()
    exit()
