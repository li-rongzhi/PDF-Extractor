from ExternalModel import ExternalModel, PromptTemplate
from PDFExtractor import PDFExtractor
import os
"""
Annex A... -- plain table
Basic... -- plain text
mndsste... -- plain text
Schedules... -- graphs
Tritech... -- plain text
VIMA... -- plain text   footnotes
"""

files = ['Tritech Announcement (MOU-NUS) 21 Nov 2008',
         'VIMA - Model Non-Disclosure Agreement (22.11.2019)',
         'Basic-Non-Disclosure-Agreement', 'mndsstecmou_annex',
         'Annex A - List of MOUs signed at the 3rd SCI JIC Meeting',
         'Schedules-to-MOU']
dir_path = "testcases/inputs"
files = list(map(lambda file_name: "testcases/inputs/" + file_name, os.listdir(dir_path)[3:]))
PDFExtractor.pipeline(*files)
"""
The following part restructure the text extracted from images in pdf file --- Schedule-to-MOU
Due to dynamic responses from external model, 
it is hard to always use a general way to manipulate response in csv format and write into an Excel file.
"""
with open("apikey.txt", "r") as file:
    key = file.read()
model = ExternalModel(key)
PDFExtractor.restructure_tables(
    [f"testcases/outputs/Schedules-to-MOU/text_from_images/{i}_1.txt" for i in range(1, 3)],
    "testcases/outputs/Schedules-to-MOU/table_from_img1-2.xlsx", model)
