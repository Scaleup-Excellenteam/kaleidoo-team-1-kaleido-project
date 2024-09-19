import os
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.csv import partition_csv
from unstructured.partition.text import partition_text
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.json import partition_json
from unstructured.partition.xml import partition_xml
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.epub import partition_epub
from unstructured.partition.msg import partition_msg
from unstructured.partition.rst import partition_rst

import os
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.csv import partition_csv
from unstructured.partition.text import partition_text
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.json import partition_json
from unstructured.partition.xml import partition_xml
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.epub import partition_epub
from unstructured.partition.msg import partition_msg
from unstructured.partition.rst import partition_rst

def partition_file(file_path):
    """Partition a file based on its extension."""
    _, ext = os.path.splitext(file_path)
    
    if ext == '.pdf':
        return partition_pdf(file_path)
    elif ext == '.doc':
        return partition_doc(file_path)
    elif ext == '.csv':
        return partition_csv(file_path)
    elif ext == '.txt':
        return partition_text(file_path)
    elif ext == '.docx':
        return partition_docx(file_path)
    elif ext == '.html':
        return partition_html(file_path)
    elif ext == '.pptx':
        return partition_pptx(file_path)
    elif ext == '.json':
        return partition_json(file_path)
    elif ext == '.xml':
        return partition_xml(file_path)
    elif ext == '.xlsx':
        return partition_xlsx(file_path)
    elif ext == '.epub':
        return partition_epub(file_path)
    elif ext == '.msg':
        return partition_msg(file_path)
    elif ext == '.rst':
        return partition_rst(file_path)
    else:
        raise ValueError(f"No partitioner found for file type: {ext}")

# Example usage:
# result = partition_file('example.pdf')
