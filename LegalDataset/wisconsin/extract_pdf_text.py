# NOTE - Obsolete. INstead, Use linux command 
# pdftotext ../nogit_data/text.pdf ../nogit_data/text.txt
# Faster and slightly cleaner output

import typing
from pathlib import Path

from borb.pdf import Document
from borb.pdf import Page
from borb.toolkit import SimpleTextExtraction
#from borb.pdf import SingleColumnLayout
#from borb.pdf import Paragraph
from borb.pdf import PDF


# NOTE: Inside ../nogit_data:
# curl https://online.drl.wi.gov/decisions/2016/ORDER0004812-00012863.pdf -o no_text_annot.pdf -C -
# curl https://online.drl.wi.gov/decisions/2015/ORDER0004379-00012032.pdf
# -o annotated.pdf -C -
# curl https://online.drl.wi.gov/decisions/2020/ORDER0006966-00016969.pdf -o incorrect_text_annot.pdf -C -

# NOTE: Borb documentation:
# https://stackabuse.com/automating-processing-pdf-invoices-in-python-with-borb/
def read_modified_document():
    # read the Document
    doc: typing.Optional[Document] = None
    l: SimpleTextExtraction = SimpleTextExtraction()

    with open("../nogit_data/incorrect_text_annot.pdf", "rb") as in_file_handle:
        doc = PDF.loads(in_file_handle, [l])

    # check whether we have read a Document
    assert doc is not None

    # print the \Producer key from the \Info dictionary
    print("PDF metadata, Producer: %s" % doc.get_document_info().get_producer())
    print(f'Num. of pages: {len(l.get_text())}')
    for i, page in l.get_text().items():
        print(f'\n\t\t === Extracted text from page {i}: ===')
        print(page[:500])

    with open("../nogit_data/incorrect_text_annot_borb.txt", "w") as outfile:
        for i, page in l.get_text().items():
            outfile.write(page)
    return l

read_modified_document()
