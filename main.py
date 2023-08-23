from PDFExtractor import PDFExtractor

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

params = list(map(lambda file: "testcases/inputs/" + file + ".pdf", files))
PDFExtractor.pipeline(*params)
