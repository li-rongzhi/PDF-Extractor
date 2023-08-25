from ExternalModel import ExternalModel
from PDFExtractor import PDFExtractor
import os

"""
Testcase analysis:
Annex A... -- table
Basic... -- text
mndsste... -- text
Schedules... -- graphs
Tritech... -- text
VIMA... -- text with footnotes
"""


def main():
    dir_path = "testcases/inputs"
    files = list(map(lambda file_name: "testcases/inputs/" + file_name, os.listdir(dir_path)))
    PDFExtractor.pipeline(*files)
    # extra_process()


if __name__ == "__main__":
    main()


def extra_process():
    """
    The following part restructures the text extracted from images in PDF file --- Schedule-to-MOU
    Due to dynamic responses from the external model,
    it is hard to always use a general way to manipulate responses in csv format and write them into an Excel file.
    """
    with open("apikey.txt", "r") as file:
        key = file.read()
    model = ExternalModel(key)
    PDFExtractor.restructure_tables(
        [f"testcases/outputs/Schedules-to-MOU/text_from_images/{i}_1.txt" for i in range(1, 3)],
        "testcases/outputs/Schedules-to-MOU/table_from_img1-2.xlsx", model)
