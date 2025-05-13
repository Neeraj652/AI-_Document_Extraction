import os
import re
import uuid
import spacy
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageEnhance
import pytesseract
import pdf2image
import docx2txt
import fitz
from typing import Dict, List, Tuple
import nltk
import logging


nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")


app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

STATE_MAPPING = {
    'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
    'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
    'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
    'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
    'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
    'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI', 'WYOMING': 'WY'
}

class DocumentAnalyzer:
    def __init__(self, text: str):
        self.text = text
        self.doc = nlp(text)
        self.lines = [line.strip() for line in text.splitlines() if line.strip()]
        logging.info("DocumentAnalyzer initialized with text length: %d", len(text))
        # Debug: Log first few lines of text
        logging.debug("First few lines of text:")
        for line in self.lines[:5]:
            logging.debug(line)

    def _validate_name(self, name: str) -> bool:
        """Improved name validation"""
        if not name:
            return False
            
        # Reject common false positives
        invalid_terms = [
            'licensee', 'search', 'details', 'profile', 'license',
            'verification', 'portal', 'system', 'database'
        ]
        
        name_lower = name.lower()
        if any(term in name_lower for term in invalid_terms):
            logging.debug(f"Name rejected due to invalid terms: {name}")
            return False
            
        # Must have at least two parts and not be too long
        parts = name.split()
        if len(parts) < 2 or len(parts) > 5:
            return False
            
        # At least one part must be longer than 1 character
        if not any(len(part) > 1 for part in parts):
            return False
            
        # Should not contain numbers or special characters
        if re.search(r'[0-9@#$%^&*()_+=\[\]{};\'\"\\|<>?]', name):
            return False
            
        return True

    def _clean_provider_name(self, name: str) -> str:
        """Improved name cleaning"""
        if not name:
            return ""

        # Remove surrounding whitespace first
        name = name.strip()

        # Remove common titles and credentials with their variations
        name = re.sub(r'(?i)^(dr\.?|doctor|prof\.?|professor)\s+', '', name)
        
        # Handle credentials at the end
        name = re.sub(r'(?i),?\s*(md|do|phd|mph|ms|m\.d\.?|d\.o\.?|country|state).*$', '', name)
        
        # Handle comma-separated format (Last, First)
        if ',' in name:
            parts = name.split(',', 1)
            if len(parts) == 2:
                last_name = parts[0].strip()
                first_name = parts[1].strip()
                name = f"{first_name} {last_name}"

        # Normalize whitespace
        name = ' '.join(name.split())

        # Convert to title case if all caps
        if name.isupper():
            name = name.title()

        return name if self._validate_name(name) else ""

    def _standardize_date(self, date_str: str) -> str:
        """Enhanced date standardization"""
        try:
            # Remove any surrounding whitespace
            date_str = date_str.strip()
            
            # Handle written month format
            if re.match(r'[A-Za-z]+', date_str):
                try:
                    return datetime.strptime(date_str, '%B %d, %Y').strftime('%m-%d-%Y')
                except ValueError:
                    try:
                        return datetime.strptime(date_str, '%b %d, %Y').strftime('%m-%d-%Y')
                    except ValueError:
                        pass

            # Handle numeric formats
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                return ""

            if len(parts) == 3:
                month, day, year = map(int, parts)
                
                # Handle two-digit years
                if year < 100:
                    year = 2000 + year if year < 50 else 1900 + year
                
                # Validate date components
                if not (1 <= month <= 12 and 1 <= day <= 31):
                    return ""
                    
                return f"{month:02d}-{day:02d}-{year}"

        except Exception as e:
            logging.error(f"Error standardizing date {date_str}: {str(e)}")
            return ""

        return ""
    def extract_provider_name(self) -> Tuple[str, float]:
        """Enhanced name extraction with better pattern matching"""
        name_patterns = [
            # Exact field matches (highest confidence)
            (r'Name:\s*([^:\n]+?)(?=\s*(?:Designation|Lic #|MD|DO|$))', 0.95),
            (r'Name on License:\s*([^:\n]+)', 0.95),
            (r'Licensee Name:\s*([^:\n]+)', 0.95),
            # Profile headers
            (r'Profile for\s+([^:\n]+?)(?=\s*$)', 0.90)
        ]

        # Try exact field patterns first
        for pattern, conf in name_patterns:
            match = re.search(pattern, self.text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = self._clean_provider_name(match.group(1))
                if name and self._validate_name(name):
                    logging.info(f"Provider name found using pattern: {name}")
                    return name, conf

        # Fallback to scanning each line for name-like patterns
        for line in self.lines[:10]:  # Check first 10 lines
            if ':' in line:
                label, value = line.split(':', 1)
                label = label.strip().lower()
                if 'name' in label and 'file' not in label:
                    name = self._clean_provider_name(value)
                    if name and self._validate_name(name):
                        logging.info(f"Provider name found in line scan: {name}")
                        return name, 0.90

        # Last resort: NLP with stricter validation
        person_entities = [ent for ent in self.doc.ents if ent.label_ == 'PERSON']
        for entity in person_entities:
            name = self._clean_provider_name(entity.text)
            if name and self._validate_name(name):
                logging.info(f"Provider name found using NLP: {name}")
                return name, 0.85

        logging.warning("No valid provider name found")
        return "", 0.0

    def extract_state_code(self) -> Tuple[str, float]:
        """Extract state code using patterns found in real documents"""
        
        # Check for state name in header
        header_pattern = r'(?:Department of Health|Medical Board|DHHS|DOH)\s+(?:of\s+)?([A-Za-z\s]+)'
        match = re.search(header_pattern, ' '.join(self.lines[:5]), re.IGNORECASE)
        if match:
            state_name = match.group(1).strip().upper()
            if state_name in STATE_MAPPING:
                logging.info(f"State found in header: {STATE_MAPPING[state_name]}")
                return STATE_MAPPING[state_name], 1.0

        # Check for explicit state mentions
        for state_name, code in STATE_MAPPING.items():
            if re.search(rf"\b{state_name}\b", self.text, re.IGNORECASE):
                logging.info(f"State found (explicit): {code}")
                return code, 1.0

        # Check for state codes in address
        address_pattern = r'[A-Z\s]+,\s*([A-Z]{2})\s*\d{5}'
        match = re.search(address_pattern, self.text)
        if match:
            state_code = match.group(1)
            if state_code in STATE_MAPPING.values():
                logging.info(f"State found in address: {state_code}")
                return state_code, 0.95

        logging.warning("No state code found")
        return "UNKNOWN", 0.0

    def extract_expiration_date(self) -> Tuple[str, float]:
        """Enhanced date extraction with debug logging"""
        date_patterns = [
            # License expiration formats
            (r'License Expiration Date:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            (r'Expires:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            (r'Expiration:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            (r'Date of Expiration:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            # Cancellation/end date formats
            (r'License Cancellation Date:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            (r'Valid Through:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.95),
            # More flexible patterns
            (r'(?:expires|expiration|valid through|valid until)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', 0.90),
            # Handle written month format
            (r'(?:expires|expiration|valid through|valid until)[:\s]*([A-Za-z]+\s+\d{1,2},?\s*\d{4})', 0.90)
        ]

        # Debug: Log lines containing date-related keywords
        for line in self.lines:
            if any(keyword in line.lower() for keyword in ['expir', 'valid', 'date']):
                logging.debug(f"Potential date line found: {line}")

        for pattern, conf in date_patterns:
            match = re.search(pattern, self.text, re.MULTILINE | re.IGNORECASE)
            if match:
                date_str = match.group(1)
                formatted_date = self._standardize_date(date_str)
                if formatted_date:
                    logging.info(f"Expiration date found: {formatted_date} (from {date_str})")
                    return formatted_date, conf

        # Fallback: Look for dates near expiration keywords
        exp_keywords = ['expir', 'valid through', 'valid until']
        for line in self.lines:
            if any(keyword in line.lower() for keyword in exp_keywords):
                # Look for date patterns in this line
                date_matches = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', line)
                for date_str in date_matches:
                    formatted_date = self._standardize_date(date_str)
                    if formatted_date:
                        logging.info(f"Expiration date found (fallback): {formatted_date}")
                        return formatted_date, 0.85

        logging.warning("No expiration date found")
        return "Date not found", 0.0
    def classify_document_type(self) -> Tuple[str, float]:
        """Enhanced document classification"""
        type_patterns = {
            'State Medical License': [
                (r'medical\s+license\b', 0.95),
                (r'physician\s+license\b', 0.95),
                (r'license\s+to\s+practice\s+medicine', 0.95),
                (r'state\s+(?:medical|physician)\s+board', 0.90),
                (r'composite\s+medical\s+board', 0.90)
            ],
            'Board Certification': [
                (r'board\s+certi(?:fied|fication)\b', 0.95),
                (r'specialty\s+board\s+certification', 0.95),
                (r'american\s+board\s+of', 0.90),
                (r'ABOS', 0.90)
            ],
            'DEA License': [
                (r'DEA\s+registration', 0.95),
                (r'drug\s+enforcement\s+administration', 0.95),
                (r'controlled\s+substance\s+registration', 0.95)
            ]
        }

        # Debug: Log document classification attempts
        logging.debug("Analyzing document type...")
        for line in self.lines[:10]:
            logging.debug(f"Checking line: {line}")

        for doc_type, patterns in type_patterns.items():
            for pattern, conf in patterns:
                if re.search(pattern, self.text, re.IGNORECASE):
                    logging.info(f"Document classified as: {doc_type}")
                    return doc_type, conf

        logging.info("Document classified as Other Certificate")
        return "Other Certificate", 0.60


def preprocess_image_for_ocr(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    return image


def extract_text_from_image(image):
    image = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(image)
    logging.info("Text extracted from image with OCR, length: %d", len(text))
    return text


def extract_text_from_pdf(file_path):
    text_from_pymupdf = ""
    text_from_ocr = ""
    
    try:
        # Attempt extraction with PyMuPDF
        doc = fitz.open(file_path)
        for page in doc:
            text_from_pymupdf += page.get_text()
        doc.close()
    except Exception as e:
        logging.warning("PyMuPDF extraction failed: %s", e)

    if not text_from_pymupdf.strip():
        # If no text from PyMuPDF, use OCR
        pages = pdf2image.convert_from_path(file_path)
        for page in pages:
            text_from_ocr += extract_text_from_image(page) + "\n"
    
    combined_text = text_from_pymupdf + text_from_ocr
    logging.info("Combined text length from PDF extraction: %d", len(combined_text))
    return combined_text


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error("No file uploaded.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected.")
        return jsonify({"error": "No file selected"}), 400

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in {'.jpg', '.jpeg', '.png', '.pdf', '.docx'}:
        logging.error("Unsupported file type: %s", file_extension)
        return jsonify({"error": "Unsupported file type"}), 400

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    logging.info("File saved: %s", file_path)

    text = extract_text_from_pdf(file_path) if file_extension == '.pdf' else extract_text_from_image(Image.open(file_path))
    if not text.strip():
        logging.error("Failed to extract text from document.")
        return jsonify({"error": "Failed to extract text from document"}), 500

    analyzer = DocumentAnalyzer(text)
    provider_name, name_conf = analyzer.extract_provider_name()
    state_code, state_conf = analyzer.extract_state_code()
    doc_type, type_conf = analyzer.classify_document_type()
    expiration_date, date_conf = analyzer.extract_expiration_date()

    response_data = {
        "provider": provider_name,
        "documentName": f"{state_code} - {doc_type} ({uuid.uuid4().hex[:8]})",
        "documentType": doc_type,
        "category": doc_type,
        "expirationDate": expiration_date,
        "stateCode": state_code,
        "confidence_scores": {
            "state": state_conf,
            "provider": name_conf,
            "type": type_conf,
            "date": date_conf
        }
    }

    logging.info("Response data: %s", response_data)
    os.remove(file_path)
    return jsonify(response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    

