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

# Mapping file extensions to partition functions
file_partitioners = {
    '.pdf': partition_pdf,
    '.doc': partition_doc,
    '.csv': partition_csv,
    '.txt': partition_text,
    '.docx': partition_docx,
    '.html': partition_html,
    '.pptx': partition_pptx,
    '.json': partition_json,
    '.xml': partition_xml,
    '.xlsx': partition_xlsx,
    '.epub': partition_epub,
    '.msg': partition_msg,
    '.rst': partition_rst,
}

def partition_file(file_path):
    """Partition a file based on its extension."""
    _, ext = os.path.splitext(file_path)
    partitioner = file_partitioners.get(ext)
    if partitioner is None:
        raise ValueError(f"No partitioner found for file type: {ext}")
    return partitioner(file_path)
