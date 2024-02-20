from helpers.util import print_time
import os
import time
import warnings
from langchain.document_loaders import BSHTMLLoader


def get_doc_dailymed(setid, method="xml", _logger=None):
    """Get the Document from DailyMed

    Parameters
    ----------
    setid : str
        internal id of drug to extract XML
    method : str
        extraction method used, option: "xml", "pdf", "url"
    _logger : logging
        logger file or type logging for debug | error | warning | info

    Returns
    -------
    filename of extracted XML from DailyMed website or 'None' in case of error
    """

    import requests
    from zipfile import ZipFile
    from io import BytesIO

    BASE_XML_URL = f"https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid={setid}&type=zip"
    BASE_PDF_URL = f"https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid={setid}&type=pdf"
    BASE_WEB_URL = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"

    start = time.time()
    if _logger:
        _logger.info(f'Extracting {method} from ID: {setid}')

    poss_methods = ['xml', 'pdf', 'both', 'url']
    assert method in poss_methods, "Make sure you select one of the following options: " + ", ".join(poss_methods)

    output = None
    try:
        if method == 'xml':
            r = requests.get(BASE_XML_URL)
            z = ZipFile(BytesIO(r.content))
            xml_content = "\n".join([z.read(name).decode() for name in z.namelist() if name.endswith('.xml')])
            
            filename = f"{os.environ['LOG_DIR']}{setid}.xml"
            
            try:
                with open(filename, 'w+', encoding='utf8') as f:
                    f.write(xml_content)
            except Exception as e:
                print("Error writing XML content to file:", e)        

            output = filename
        elif method == 'url':
            output = BASE_WEB_URL
        elif method == 'pdf':
            r = requests.get(BASE_PDF_URL)
            filename = f'/tmp/{setid}.pdf'
            with open(filename, 'wb') as f:
                f.write(r.content)

            output = filename
        elif method == 'both':
            r_pdf = requests.get(BASE_PDF_URL)
            filename_pdf = f'/tmp/{setid}.pdf'
            with open(filename_pdf, 'wb') as f:
                f.write(r_pdf.content)

            r_xml = requests.get(BASE_XML_URL)
            z = ZipFile(BytesIO(r_xml.content))
            xml_content = "\n".join([z.read(name).decode() for name in z.namelist() if name.endswith('.xml')])
            filename_xml = f'/tmp/{setid}.xml'
            with open(filename_xml, 'w+') as f:
                f.write(xml_content)

            output = [filename_pdf, filename_xml]

        if _logger:
            _logger.info(f'Finishing extracting {method}')
            _logger.info(f'Took overall: {print_time(time.time() - start)}\n')

        return output
    except Exception as e:
        if _logger:
            _logger.error(f"Error processing {setid}. Exception: '{e.__str__()}'")
            _logger.info(f'Took overall: {print_time(time.time() - start)}\n')
        return None


def custom_clean_txt(txt):
    """ Clean text of extra spaces, lines

    Parameters
    ----------
    txt : strt
        original text

    Returns
    -------
        trimed text
    """

    import re

    txt = re.sub("\<.*?\>", "", txt)
    txt = re.sub(r"[\xa0]+", " ", txt)
    txt = re.sub(r"([ ]{2,})", " ", txt)
    txt = re.sub(r"[ ]\n", "\n", txt)
    txt = re.sub(r"\n[ ]", "\n", txt)
    txt = re.sub(r"\n\n\n+", "\n\n", txt)

    return txt


def extract_xml(filename, method):
    """ Extract XML from a filename with different methods

    Parameters
    ----------
    filename : str
        filename of the XML wanting to extract the information
    method : char
        the different method of extracting. 1 - UnstructuredXMLLoader; 2 - XML ;  3 - HTML5

    Returns
    -------
    txt : str
        the content of the parsed XML
    document_xml : llama_index.schema.Document
        the Document object
    """
    from langchain.document_loaders import UnstructuredXMLLoader
    from llama_index import Document

    if method == '1':
        loader = UnstructuredXMLLoader(filename)
        docs = loader.load()
        txt = docs[0].page_content
        document_xml = Document(text=txt)
    elif method == '2':
        '''loader = BSHTMLLoader(filename, bs_kwargs={'features': 'xml'})
        docs = loader.load()
        txt = docs[0].page_content

        document_xml = Document(text=txt)'''

        with open(filename, 'r', encoding='utf-8') as file:
            txt = file.read()

        document_xml = Document(text=txt)
        
    elif method == '3':
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loader = BSHTMLLoader(filename, bs_kwargs={'features': 'html5lib'})
            docs = loader.load()
        txt = docs[0].page_content
        txt = custom_clean_txt(txt)

        document_xml = Document(text=txt)
    else:
        txt = ""
        document_xml = Document(text=txt)

    return txt, document_xml


def extract_doc_content(doc_filename, _logger=None):
    """

    Parameters
    ----------
    doc_filename : str
        xml filename to load
    _logger : logging
        logger file or type logging for debug | error | warning | info

    Returns
    -------
    document_xml : llama_index.schema.Document
        the Document object
    """

    from pathlib import Path
    from llama_index import download_loader

    content, index = "", None
    document_xml, document_pdf = None, None
    
    start = time.time()
    if _logger:
        _logger.info(f'Loading XML filename: {doc_filename}')

    try:
        content_pdf, content_xml = "", ""

        if isinstance(type(doc_filename), list):
            method_xml = any([f.endswith('.xml') for f in doc_filename])
            method_pdf = any([f.endswith('.pdf') for f in doc_filename])
        else:
            method_xml = doc_filename.endswith('.xml')
            method_pdf = doc_filename.endswith('.pdf')

        if method_xml:
            if isinstance(type(doc_filename), list):
                doc_filename_xml = [f for f in doc_filename if f.endswith('.xml')][0]
            else:
                doc_filename_xml = doc_filename

            content_xml, document_xml = extract_xml(doc_filename_xml, os.environ['XML_EXTRACTION'])

        if method_pdf:
            PDFReader = download_loader("PDFReader")

            loader = PDFReader()
            if isinstance(type(doc_filename), list):
                doc_filename_pdf = [f for f in doc_filename if f.endswith('.pdf')][0]
            else:
                doc_filename_pdf = doc_filename
            document_pdf = loader.load_data(file=Path(doc_filename_pdf))
            document_pdf = document_pdf[0]
            document_pdf.id_ = doc_filename_pdf if isinstance(type(doc_filename_pdf), str) else doc_filename_pdf[0]
            content_pdf = document_pdf.text

        max_content = max([len(content_xml), len(content_pdf)])

        if len(content_xml) == max_content:
            doc_to_index = document_xml
        elif len(content_pdf) == max_content:
            doc_to_index = document_pdf
        else:
            doc_to_index = document_xml

        doc_to_index = doc_to_index if isinstance(doc_to_index, list) else [doc_to_index]

        if _logger:
            _logger.info(f'Finished loading content.')
            _logger.info(f'Took overall: {print_time(time.time() - start)}\n')

        return doc_to_index
    except Exception as e:
        if _logger:
            _logger.error(f"Error loading XML filename: {doc_filename}. Error: '{e.__str__()}'")
            _logger.info(f'Took overall: {print_time(time.time() - start)}\n')
        else:
            print(f"Error loading XML filename: {doc_filename}. Error: '{e.__str__()}'")
            print(f'Took overall: {print_time(time.time() - start)}\n')

        return None
