import PDFExtractor

"""
Annex A... -- plain table with headings
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
         'Schedules-to-MOU', 'L00_module_info',
         'ImageNet classification with deep convolutional neural networks', 'combinepdf']
file_name = files[4]
pdf_path = f'venv/testcases/inputs/{file_name}.pdf'
output_path = f'venv/testcases/outputs/{file_name}.txt'

output_dir = "venv/testcases/outputs/Schedules_to_MOU"
output_excel = f"venv/testcases/outputs/{file_name}.xlsx"
# footnotes = PDFExtractor.extract_footnotes(pdf_path)
# print(footnotes)
# text = PDFExtractor.extract_text(pdf_path, output_path)
# # print(text)
# for footnote in footnotes:
#     if footnote in text:
#         print(footnote)
#         print(True)
#         text = text.replace(footnote, "")
# print(text)
texts = PDFExtractor.extract_text(pdf_path, output_path)
print(texts)

print("/////")
print("\n"*3)
table_contents = PDFExtractor.extract_tables(pdf_path, output_path)
print(table_contents)
print("/////")
print("\n"*3)
for content in table_contents:
    if content in texts:
        print(content)
        texts = texts.replace(content, "")
print("/////")
print("\n"*3)
print(texts)