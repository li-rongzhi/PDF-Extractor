from collections import Counter
import PyPDF2
import pandas as pd
from tabula import read_pdf
import fitz
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar, LTImage, LTFigure
import openpyxl
from ExternalModel import ExternalModel, PromptTemplate
from OCR import OCR


class PDFExtractor:
    """A PDF extractor for extracting contents from PDF files"""

    @staticmethod
    def extract_text(pdf_path, output_path, contents, externalModel=None):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            with open(output_path, 'a', encoding="utf-8") as output_file:
                # extract footnotes in the pdf file
                footnotes = PDFExtractor.extract_footnotes(pdf_path)
                # iterate through pages of the pdf file
                for page_num in range(len(pdf_reader.pages)):
                    # extract text from current page
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    # get footnotes of the current page
                    current_page = footnotes[str(page_num)]

                    # use external model to correct grammar and spelling
                    # in case of random errors when extracting text
                    if externalModel:
                        text = externalModel.get_response(text, PromptTemplate.GRAMMAR_CORRECTION)

                    # delete footnotes from the text
                    # if there are footnotes in current page
                    if current_page:
                        for footnote in footnotes:
                            if footnote in text:
                                text = text.replace(footnote, "")

                    for content in contents:
                        if content in text:
                            text = text.replace(content, "")
                    # write into the output file
                    output_file.write(f"Page {page_num + 1}:\n{text}\n")
                    # add the footnotes
                    if current_page:
                        output_file.write(
                            "Footnotes:\n" + "\n".join(f"{i+1}:{note}"
                                                       for i, note in enumerate(current_page))+"\n\n")

        except FileNotFoundError:
            # handle file not found error
            print("File not found")

    @staticmethod
    def extract_tables(pdf_path, output_path, externalModel=None, set_wrap_text=False):
        """Extract tables from PDF file"""
        try:
            # extract tables directly using tabula.read_pdf
            tables = read_pdf(
                pdf_path, pages='all', multiple_tables=True, guess=False, lattice=True)
            results = []
            # iterate through all tables
            for table in tables:
                # skip if got nothing
                if table.empty:
                    continue
                table = table.reset_index(drop=True)
                new_table = pd.DataFrame(columns=table.columns)
                start = 0
                indexes = []

                # iterate through each line
                for index in range(len(table)):
                    # if all cells are NaN in one line
                    # consider it as a split of rows
                    # same if reach the end of the table
                    if table.iloc[index].isna().all() or index == len(table) - 1:
                        # then merge lines into one row
                        concatenated = table.iloc[start:index + 1].apply(
                            lambda row: ' '.join(map(str, row.dropna())), axis=0)
                        new_row = pd.DataFrame([concatenated.tolist()], columns=table.columns)
                        new_table = pd.concat([new_table, new_row], ignore_index=True)
                        start = index + 1

                # assume that all cells should be filled up
                # if got cell with "" value
                # merge values in other cells in the same row with the above row
                for index, row in new_table.iterrows():
                    if (row == "").any():
                        indexes.append(index)
                        concatenated = new_table.iloc[index - 1:index + 1].apply(
                            lambda row: ' '.join(map(str, row.dropna())), axis=0)
                        new_row = pd.DataFrame([concatenated.tolist()], columns=new_table.columns)
                        new_table[index - 1:index] = new_row
                # if drop raws
                # then reset index for the table in case of random error
                if indexes:
                    new_table.drop(indexes, inplace=True)
                    new_table.reset_index(drop=True, inplace=True)

                # if externalModel is passed into the method
                if externalModel:
                    # check if the headers of the table are real headers
                    cols = list(table.columns)
                    is_header = externalModel.get_response("; ".join(cols), PromptTemplate.ISHEADER_CHECK) in ("Yes", "Yes.")

                    # if they don't seem to be header
                    # check if it should combine with the last row of previous table
                    # or the first row of the current table
                    if not is_header:
                        combine_with_previous = False
                        # combine column names(headers) with values in the first row
                        # and then send to the external model
                        cols_and_next = [f"{col} {val}" for col, val in zip(new_table.columns, new_table.iloc[0])]
                        answer_next = [externalModel.get_response(pair, PromptTemplate.CONSISTENCY_CHECK)
                                for pair in cols_and_next]
                        combine_with_next = all([ans in ("Yes.", "Yes") for ans in answer_next])
                        # if there is previous tables and number of columns are the same
                        if results and (len(results[-1].columns) == len(new_table.columns)):
                            # combine column names(headers) with values in the last row of previous table
                            cols_and_previous = [f"{val} {col}"
                                                 for val, col in zip(results[-1].iloc[-1], new_table.columns)]
                            answer_previous = [externalModel.get_response(pair, PromptTemplate.CONSISTENCY_CHECK)
                                   for pair in cols_and_previous]
                            combine_with_previous = all([ans in ("Yes.", "Yes") for ans in answer_previous])

                        # if headers need to combine with both
                        if combine_with_previous and combine_with_next:
                            triple = [f"{prev} {curr}" for prev, curr in zip(cols_and_previous, new_table.iloc[0])]
                            new_row = pd.DataFrame([triple], columns=results[-1].columns)
                            new_table.columns = results[-1].columns
                            new_table = pd.concat([results[-1].iloc[:-1], new_row, new_table[1:]], ignore_index=True)
                            results.pop()
                        # if headers need to combine with last row in previous table only
                        elif combine_with_previous:
                            new_row = pd.DataFrame([cols_and_previous], columns=results[-1].columns)
                            new_table.columns = results[-1].columns
                            new_table = pd.concat([results[-1].iloc[:-1], new_row, new_table], ignore_index=True)
                            results.pop()
                        # if headers need to combine with first row in current table only
                        elif combine_with_next:
                            new_row = pd.DataFrame([cols_and_next], columns=range(1, len(new_table.columns) + 1))
                            new_table = pd.concat([new_row, new_table[1:]], ignore_index=True)
                results.append(new_table)
            # write tables into Excel as one table per sheet
            with pd.ExcelWriter(output_path) as writer:
                for i, table in enumerate(results):
                    table.to_excel(writer, sheet_name=f'Sheet{i}', index=False)

            # set cells attribute wrapText=True for usability
            contents = []
            if set_wrap_text:
                workbook = openpyxl.load_workbook(output_path)
                # loop through all cells with content in the worksheet
                for sheet_name in workbook.sheetnames:
                    worksheet = workbook[sheet_name]
                    for row in worksheet.iter_rows():
                        for cell in row:
                            if cell.value is not None:
                                contents.append(cell.value)
                                cell.alignment = openpyxl.styles.Alignment(wrapText=True)
                # save the modified workbook (overwriting the original file)
                workbook.save(output_path)
            return contents
        except FileNotFoundError:
            print("File not found")

    @staticmethod
    def locate_images(pdf_path):

        def extract_LTImage_from_LTFigure(page_number, element):
            results = []
            for item in element:
                if isinstance(item, LTImage):
                    results.append((page_number, item))
                elif isinstance(item, LTFigure):
                    results.extend(extract_LTImage_from_LTFigure(page_number, item))
            return results

        pages_contain_image = []
        for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
            for element in page_layout:
                if isinstance(element, LTImage):
                    pages_contain_image.append(page_number)
                    break
                elif isinstance(element, LTFigure):
                    temp = extract_LTImage_from_LTFigure(page_number, element)
                    if len(temp) > 0:
                        pages_contain_image.append(page_number)
                        break
        return pages_contain_image

    @staticmethod
    def extract_images(pdf_path, output_folder):
        """Extract images from PDF file"""
        try:
            pdf_document = fitz.open(pdf_path)
            # get an array of page numbers
            # for pages containing at least one images
            page_numbers = PDFExtractor.locate_images(pdf_path)
            # iterate through those pages
            for page_number in page_numbers:
                page = pdf_document[page_number - 1]
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_data = base_image["image"]
                    image_type = base_image["ext"]
                    with open(f"{output_folder}/{page_number + 1}_{img_index + 1}.{image_type}",
                              "wb") as img_file:
                        img_file.write(image_data)
            pdf_document.close()
        except FileNotFoundError:
            print("File not found")

    @staticmethod
    def extract_text_from_images(images_container, output_folder):
        OCR.extract_in_batch(images_container, output_folder)

    @staticmethod
    def extract_footnotes(pdf_path, font_size_threshold_factor=0.95, height_threshold_factor=0.2):
        font_sizes = []
        # iterate through elements in each page
        # record font sizes
        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    font_sizes.append(character.size)
                                    break
        # calculate the most common font size as the size for body
        font_size_counter = Counter(font_sizes)
        most_common_font_size = font_size_counter.most_common(1)[0][0]
        # use a factor to set a threshold for font size of footnotes
        footnote_font_size_threshold = most_common_font_size * font_size_threshold_factor
        # create a dictionary to hold footnotes in different pages
        footnotes = {}
        # iterate again to extract footnotes
        # check if font size and position satisfy the condition
        # if so, extract that part and add into footnotes
        page_number = 0
        for page_layout in extract_pages(pdf_path):
            current_page = []
            page_height = page_layout.height
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    font_size = character.size
                                    break
                            y_position = text_line.y0
                            text = text_line.get_text().strip()
                            foot_note_height_threshold = page_height * height_threshold_factor
                            if font_size <= footnote_font_size_threshold and y_position <= foot_note_height_threshold:
                                current_page.append(text)
            footnotes[f'{page_number}'] = current_page
            page_number += 1
        return footnotes


files = ['Tritech Announcement (MOU-NUS) 21 Nov 2008',
         'VIMA - Model Non-Disclosure Agreement (22.11.2019)',
         'Basic-Non-Disclosure-Agreement', 'mndsstecmou_annex',
         'Annex A - List of MOUs signed at the 3rd SCI JIC Meeting',
         'Schedules-to-MOU', 'L00_module_info',
         'ImageNet classification with deep convolutional neural networks', 'combinepdf']
file_name = files[4]
pdf_path = f'testcases/inputs/{file_name}.pdf'
output_path = f'testcases/outputs/{file_name}.txt'

output_dir = "testcases/outputs/Schedules_to_MOU"
output_excel = f"testcases/outputs/{file_name}.xlsx"

model = ExternalModel("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")
# content = """Copyright © 20 20 NonDisclosureAgreement.com . All Rights Reserved.  Page 1 of 2 NON -DISCLOSURE AGREEMENT  (NDA)
# This Nondisclosure Agreement or ("Agreement") has been  entered into on the date of
# ______________________________ and is by and between :"""
# PDFExtractor.extract_tables(pdf_path, output_excel)
contents = PDFExtractor.extract_tables(pdf_path, "tables.xlsx", externalModel=model, set_wrap_text=True)
PDFExtractor.extract_text(pdf_path, 'table_extraction.txt', contents, externalModel=model)

