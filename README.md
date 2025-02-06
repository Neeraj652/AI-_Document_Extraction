# Advanced Document Processing System

<img src="https://github.com/user-attachments/assets/046ad8d4-aa3d-4fcf-b579-c30f9e503f69" width="600">



## Overview
The Advanced Document Processing System is a web application designed to automate document extraction, classification, and validation.

## Key Features
- **Automated Document Classification:** Uses NLP techniques to identify provider names, document types, states, expiration dates, and categories.

- **Text Extraction:** Supports OCR-based text extraction from images and scanned PDFs.
- **Drag-and-Drop File Upload:** Users can upload documents easily via a web interface.
- **Real-Time Processing:** Extracted data is processed instantly and categorized accordingly.
- **Expiration Alerts:** Users can set reminders based on document expiration dates.

## Technologies Used

### Frontend:
- **React.js:** Used for building the interactive UI.

### Backend:
- **Flask:** Serves as the backend framework for handling API requests.
- **Tesseract OCR:** Extracts text from images and scanned PDFs.
- **spaCy & NLTK:** Utilized for natural language processing and text classification.
- **PyMuPDF & pdf2image:** Parses and processes PDF documents.
- **Pillow:** Handles image processing tasks.
- **Flask-CORS:** Enables secure communication between the frontend and backend.

## How It Works
1. **Upload a Document:** Users can drag and drop or manually upload files (JPG, PNG, PDF, DOCX).
2. **OCR & Text Extraction:** The backend processes the document and extracts text using Tesseract OCR and PDF parsers.
3. **Data Processing & Classification:** The extracted text is analyzed with spaCy and NLTK to identify key details such as provider name, document type, and expiration date.
4. **Automatic Categorization:** The system assigns the document to the correct category based on predefined rules.
5. **Expiration Date Handling:** The system detects expiration dates and allows users to set reminders.
6. **Result Display:** Processed information is displayed on the frontend, where users can review and save the details.

