# Advanced Document Processing System
![1 1](https://github.com/user-attachments/assets/eb313cd2-37a8-4573-a8a6-0dd6c3c8ed95)

![1 2](https://github.com/user-attachments/assets/c0c4f668-6036-4fad-8514-757b145b8e4a)

<img width="1440" alt="Screenshot 2025-02-05 at 9 17 40 PM" src="https://github.com/user-attachments/assets/7db09db1-149b-47c2-a110-ee5b0fa9f686" />

![Final_img](https://github.com/user-attachments/assets/359a02b7-8640-481f-bd3c-bc0f8567f5a5)




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

