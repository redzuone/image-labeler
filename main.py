from PIL import Image as ImageEdit
import matplotlib.pyplot as plt
import re
import os
import shutil
from paddleocr import PaddleOCR, draw_ocr
import argparse
import logging
import io
import base64

ocr = None
show_image_flag = False

class Image:
    def __init__(self, image_path):
        self.image_path = image_path
        self.result = None
        self.confidence = None
        self.text = None
        self.image_annotated = None
        self.new_image_filename = None
        self.new_image_path = None

class ImageLabeler:
    def __init__(self):
        self.copy_mode_flag = False
        self.interactive_mode_flag = False
        self.show_image_flag = False

    def process_single_file(self, image):
        """
        Process a single image file
        """
        if not is_supported_file(image.image_path):
            logging.warning(f'File {image.image_path} is not an image')
            return
        load_model()
        try:
            self.extract_text(image)
            self.save_image_box_gui(image)
            if self.interactive_mode_flag == False:
                if self.copy_mode_flag == True:
                    self.save_image(image)
                else:
                    self.rename_file(image)
            return image
        except Exception as e:
            logging.error(f'An error occured: {e}')
            exit()
     
    def process_images_in_folder(self, image_folder_path):
        """
        Process all images in a folder
        """
        processed_images = []
        # get all files in folder
        files = os.listdir(image_folder_path)
        # loop through files
        for file in files:
            # check if file is an image
            if is_supported_file(file):
                image_path = os.path.join(image_folder_path, file)
                image = Image(image_path)
                processed_image = self.process_single_file(image)
                processed_images.append(processed_image)
            else:
                print(f'----------------------------\n{file} is not an image')
                continue
        return processed_images

    def extract_text(self, image):
        """
        Extract text from image and clean it
        """
        load_model()
        print('----------------------------\nImage: ' + image.image_path)
        image.result = ocr.ocr(image.image_path, cls=True)
        if show_image_flag == True:
            show_image(image.image_path, image.result)
        # Extract text values
        text_list = [line[1][0] for box in image.result for line in box] # bozes > 2 lines
        # Join texts into a single string
        text = ' '.join(text_list)
        logging.info(f'Recognized text: {text}')
        # confidence
        confidence_list = [line[1][1] for box in image.result for line in box]
        image.confidence = round(sum(confidence_list) / len(confidence_list), 3)
        logging.info(f'Confidence: {image.confidence}')
        # Clean text
        pattern = r'[^a-zA-Z0-9\s]'  # Regular expression pattern to match non-alphanumeric characters
        cleaned_text = re.sub(pattern, '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text) # replace multiple spaces with one
        if len(cleaned_text) > 200:
            cleaned_text = cleaned_text[:200]
        image.text = cleaned_text
        logging.info(f'Cleaned text: {image.text}')
    
    def save_image(self, image):
        """
        Save image with new name
        """
        text = image.text.replace(' ', '_') # replace spaces with underscores
        try:
            directory = os.path.dirname(image.image_path) # get directory
            output_directory = os.path.join(directory, 'output') # create output directory
            os.makedirs(output_directory, exist_ok=True) # create directory if it doesn't exist
            image.new_image_filename = text + os.path.splitext(image.image_path)[1] # new file name with extension
            logging.info(f'New file name: {image.new_image_filename}')
            image.new_file_path = os.path.join(output_directory, image.new_image_filename) # create new file path
            logging.debug(f'New file path: {image.new_file_path}')
            shutil.copy2(image.image_path, image.new_file_path) # copy file to new path
        except Exception as e:
            logging.error(f'An error occured: {e}')
            exit()

    def rename_file(self, image):
        """
        Rename file with extracted text
        """
        text = image.text.replace(' ', '_') # replace spaces with underscores
        try:
            directory = os.path.dirname(image.image_path) # get directory
            image.new_image_filename = text + os.path.splitext(image.image_path)[1] # new file name with extension
            logging.info(f'New file name: {image.new_image_filename}')
            image.new_image_path = os.path.join(directory, image.new_image_filename) # create new file path
            logging.debug(f'New file path: {image.new_image_path}')
            os.rename(image.image_path, image.new_image_path) # rename file
        except Exception as e:
            logging.error(f'An error occured: {e}')
            exit()
    
    def save_image_box_gui(self, image):
        """
        Save temp image with bounding boxes
        """
        result = image.result[0]
        image_edit = ImageEdit.open(image.image_path).convert('RGB')
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        im_show = draw_ocr(image_edit, boxes, txts, scores, font_path='Roboto-Regular.ttf')
        im_show = ImageEdit.fromarray(im_show)

        # Calculate new width based on new height and original aspect ratio
        new_height = 300
        aspect_ratio = im_show.width / im_show.height
        new_width = int(aspect_ratio * new_height)
        
        # Resize image while maintaining aspect ratio
        im_show = im_show.resize((new_width, new_height))
        im_show.save('tmp.png')
        image.image_annotated = convert_to_bytes('tmp.png')

def menu():
    """
    Display menu for command line interface
    """
    print('\n\nImage Labeler\n  1. Process a file\n  2. Process a folder\n  3. Exit\n')
    choice = input('Enter your choice: ')
    if int(choice) == 1:
        image_path = input('Enter file name: ')
        image = Image(image_path)
        processor.copy_mode_flag = False
        processor.process_single_file(image)
    elif int(choice) == 2:
        folder_name = input('Enter folder name: ')
        processor.process_images_in_folder(folder_name)
    elif int(choice) == 3:
        exit()

def is_supported_file(file_name):
    """
    Check if file is an image
    """
    supported_files = ['.jpg', '.png', '.jpeg', '.webp', '.heic']
    if file_name.endswith(tuple(supported_files)):
        return True
    else:
        return False

def load_model():
    global ocr
    if ocr is None:
        logging.info('Loading model..')
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) # need to run only once to download and load model into memory
        logging.info('Model loaded')

def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = ImageEdit.open(file_or_bytes)
    else:
        try:
            img = ImageEdit.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = ImageEdit.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), ImageEdit.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

def show_image(image):
    """
    Show image with bounding boxes using matplotlib
    """
    result = image.result
    result = result[0]
    image = ImageEdit.open(image.new_image_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='Roboto-Regular.ttf')
    im_show = ImageEdit.fromarray(im_show)
    # im_show.save('result.jpg')
    plt.imshow(im_show)
    plt.axis('off')
    plt.show()

def rename_test_files():
    folders = ['test/multiple/', 'test/']
    for folder in folders:
        folder_path = folder
        files = os.listdir(folder_path)
        supported_files = ['.jpg', '.png', '.jpeg', '.webp', '.heic']
        for i, file in enumerate(files):
            if file.endswith(tuple(supported_files)):
                # new filename
                if folder_path == 'test/':
                    new_filename = f'test{os.path.splitext(file)[1]}'
                else:
                    new_filename = f'test{i}{os.path.splitext(file)[1]}'
                os.rename(folder_path + file, folder_path + new_filename)

if __name__ == '__main__':
    rename_test_files()

    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description='Image Labeler')
    parser.add_argument('--dir', help='Folder name to process')
    parser.add_argument('--file', help='File name to process')
    parser.add_argument('--copy', help='Copy file with new filename instead of renaming', action='store_true')
    args = parser.parse_args()
    processor = ImageLabeler()
    if args.copy:
        copy_mode_flag = True

    if args.dir:
        processor.process_images_in_folder(args.dir)
    elif args.file:
        image = Image(args.file)
        processor.copy_mode_flag = False
        processor.process_single_file(image)
    else:
        menu()
    exit()
