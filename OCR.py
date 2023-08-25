import cv2
import pytesseract
import os
from ExternalModel import PromptTemplate


# Please replace the following path with your own one
# check by cmd command "brew info tesseract"(if in mac and installed using Homebrew)
# refer to the official website for more details
# https://tesseract-ocr.github.io/tessdoc/Installation.html
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


class OCR:
    """Extract text from image using OCR(tesseract)"""

    @staticmethod
    def extract_text_from_image(image, output_path, external_model=None):
        """Extract text from input image"""
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            text = pytesseract.image_to_string(img)
            # utilise external model to polish the extracted content
            if text and external_model:
                text = external_model.get_response(text, PromptTemplate.GRAMMAR_CORRECTION)
            # if there is text extracted
            if text:
                with open(output_path, 'w') as output_file:
                    output_file.write(text)
        except FileNotFoundError:
            print('Target image not found')

    @staticmethod
    def extract_in_batch(input_dir, output_dir, external_model=None):
        """Perform extract-text-from-images in batch"""
        def is_image(img_path):
            """Check if the file is an image by extension"""
            image_extensions = ['.jpg', '.jpeg', '.png']
            file_extension = os.path.splitext(img_path)[1].lower()
            return file_extension in image_extensions

        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if is_image(file_path):
                output_path = output_dir + '/' + os.path.splitext(filename)[0] + '.txt'
                OCR.extract_text_from_image(file_path, output_path, external_model)
