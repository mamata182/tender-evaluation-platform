import pytesseract
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
import os
from app.config import settings

if os.name == 'nt' and os.path.exists(settings.TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def preprocess_image(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    return image


def ocr_image(image_path):
    try:
        image = Image.open(image_path)
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6')
        return text.strip()
    except Exception as e:
        print(f"OCR failed for {image_path}: {e}")
        return ""


def ocr_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path, dpi=300)
        all_text = []
        for page_num, image in enumerate(images, 1):
            processed = preprocess_image(image)
            page_text = pytesseract.image_to_string(
                processed, config='--oem 3 --psm 6'
            )
            if page_text.strip():
                all_text.append(f"--- Page {page_num} ---\n{page_text.strip()}")
        return "\n\n".join(all_text)
    except Exception as e:
        print(f"PDF OCR failed: {e}")
        return ""