# PDF Extractor

### Description:

This PDF content extractor can extract content from PDF files, 
with mixed types of content inside, like images, text, and tables. 

After the PDF file going through the pipeline, 
the client will get a folder containing the following stuff: 
- a folder called images for extracted images; 
- a folder of text files extracted from each extracted image; 
- Excel files for tables; 
- a txt file for all texts inside the PDF file.

(ps: folder exists only if not empty)


### Installation:
1. Make sure you have all the following packages installed.
   
   ```pip install -r requirements.txt```

    - openai
    - tiktoken
    - opencv-python
    - pytesseract
    - PyPDF2
    - pandas
    - tabula
    - pdfminer.six
    - openpyxl
    - PyMuPDF
2. Install pytesseract. Step-to-step guidance could be found 
in the following link of the [Tesseract's official website](https://tesseract-ocr.github.io/tessdoc/Installation.html).
After installation, put the path to tesseract in OCR.py as indicated.
3. Get an API key on [Openai's official website](https://platform.openai.com/account/api-keys) with your own account. 
Then paste the key in [apikey.txt](apikey.txt) file without any extra information.


### Testcases:
Please refer to [testcases](testcases) folder for testcases.
Mixed types of data, including text, table, and images are contained in testcases.