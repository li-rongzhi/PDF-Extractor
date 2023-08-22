import cv2
import pytesseract
import os

from ExternalModel import PromptTemplate

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


class OCR:
    @staticmethod
    def extract_text_from_image(image, output_path, externalModel=None):
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            text = pytesseract.image_to_string(img)
            if externalModel:
                text = externalModel.get_response(text, PromptTemplate.GRAMMAR_CORRECTION)
            with open(output_path, 'w') as output_file:
                output_file.write(text)
        except FileNotFoundError:
            print('Target image not found')

    @staticmethod
    def extract_in_batch(dir, output_dir):
        def is_image(img_path):
            image_extensions = ['.jpg', '.jpeg', '.png']
            file_extension = os.path.splitext(filename)[1].lower()
            return file_extension in image_extensions

        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            if is_image(file_path):
                output_path = output_dir + '/' + os.path.splitext(filename)[0] + '.txt'
                OCR.extract_text_from_image(file_path, output_path)