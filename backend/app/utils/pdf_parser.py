import pdfplumber
import PyPDF2


def extract_text_from_pdf(pdf_path):
    text = ""
    is_scanned = False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_texts = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    page_texts.append(f"--- Page {page_num} ---\n{page_text}")
            text = "\n\n".join(page_texts)
    except Exception:
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_texts = []
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        page_texts.append(f"--- Page {page_num} ---\n{page_text}")
                text = "\n\n".join(page_texts)
        except Exception as e:
            print(f"PDF parsing failed: {e}")

    clean_text = text.replace(" ", "").replace("\n", "")
    if len(clean_text) < 100:
        is_scanned = True

    return text, is_scanned


def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception:
        pass
    return tables