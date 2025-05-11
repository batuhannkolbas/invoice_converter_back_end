import pytesseract
from PIL import Image
import spacy
import cv2
import numpy as np
from pdf2image import convert_from_path
import os

# spaCy modelini yükle
nlp = spacy.load("en_core_web_lg")

# OCR İşleme
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    processed_image = preprocess_image(image)
    text = pytesseract.image_to_string(processed_image)
    return text

def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    all_text = ""
    for img in images:
        image_np = np.array(img)
        processed_image = preprocess_image(image_np)
        text = pytesseract.image_to_string(processed_image)
        all_text += text + "\n"
    return all_text

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    else:
        return ""

def classify_text_with_spacy(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_invoice(file_path):
    text = extract_text(file_path)
    entities = classify_text_with_spacy(text)
    return text, entities
