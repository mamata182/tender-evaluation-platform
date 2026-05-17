import os
import uuid
from app.utils.ocr import ocr_image, ocr_pdf
from app.utils.pdf_parser import extract_text_from_pdf, extract_tables_from_pdf
from app.utils.docx_parser import extract_text_from_docx
from app.config import settings

SUPPORTED = {
    'pdf': 'pdf', 'docx': 'docx', 'doc': 'docx',
    'png': 'image', 'jpg': 'image', 'jpeg': 'image',
    'tiff': 'image', 'bmp': 'image',
}


def save_uploaded_file(file_content, filename, subfolder=""):
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_name)

    with open(file_path, 'wb') as f:
        f.write(file_content)

    return file_path


def detect_file_type(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return SUPPORTED.get(ext, 'unknown')


def process_document(file_path):
    filename = os.path.basename(file_path)
    file_type = detect_file_type(filename)

    result = {
        "text": "", "tables": [], "method": "",
        "confidence": 1.0, "warnings": []
    }

    try:
        if file_type == 'pdf':
            result = _process_pdf(file_path)
        elif file_type == 'docx':
            result = _process_docx(file_path)
        elif file_type == 'image':
            result = _process_image(file_path)
        else:
            result["warnings"].append(f"Unsupported: {filename}")
            result["confidence"] = 0.0
    except Exception as e:
        result["warnings"].append(f"Error: {str(e)}")
        result["confidence"] = 0.0

    return result


def _process_pdf(file_path):
    result = {
        "text": "", "tables": [], "method": "",
        "confidence": 1.0, "warnings": []
    }

    text, is_scanned = extract_text_from_pdf(file_path)

    if not is_scanned and len(text.strip()) > 100:
        result["text"] = text
        result["method"] = "direct_pdf"
        result["confidence"] = 0.95
        result["tables"] = extract_tables_from_pdf(file_path)
    else:
        ocr_text = ocr_pdf(file_path)
        result["text"] = ocr_text
        result["method"] = "ocr"
        result["confidence"] = 0.7
        result["warnings"].append("Processed via OCR")

    return result


def _process_docx(file_path):
    text = extract_text_from_docx(file_path)
    return {
        "text": text, "tables": [], "method": "docx",
        "confidence": 0.95 if text else 0.0,
        "warnings": [] if text else ["No text extracted"]
    }


def _process_image(file_path):
    text = ocr_image(file_path)
    return {
        "text": text, "tables": [], "method": "image_ocr",
        "confidence": 0.65 if text else 0.0,
        "warnings": ["Image processed via OCR"]
    }