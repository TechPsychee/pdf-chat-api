# PDF Chat API

A sophisticated FastAPI application that enables users to chat with PDF documents using Google's Gemini API. Built with FastAPI for the backend and Streamlit for the frontend.

## Features

### Core Functionality

- PDF document upload and text extraction
- Interactive chat interface using Google's Gemini API
- Text chunking and embedding processing
- Real-time chat responses based on document content

### Security

- API key authentication
- Rate limiting
- Input validation
- Error handling
- Secure file handling

### Technical Features

- Asynchronous operations
- Comprehensive logging
- File size limitations
- Caching mechanisms
- Performance optimizations

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pdf-chat-api

2. Create and activate virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Set up environment variables in .env:

envCopyAPI_KEY=your-secure-api-key
GEMINI_API_KEY=your-gemini-api-key
DEBUG=True
UPLOAD_DIR=uploads
5. Project Structure

Usage

6. Start the backend server:

uvicorn app.main:app --reload

7. Start the frontend application:

streamlit run frontend/app.py

8. Access the applications:


Frontend Interface: http://localhost:8501
API Documentation: http://localhost:8000/docs

9. API Endpoints
Upload PDF
httpCopyPOST /v1/pdf
Header: X-API-Key: your-api-key
Body: form-data
  - file: your-pdf-file
Chat with PDF
httpCopyPOST /v1/chat/{pdf_id}
Header: X-API-Key: your-api-key
Body: {
    "message": "Your question about the PDF"
}
10. Features in Detail
- PDF Processing

File validation
Text extraction
Metadata storage
Chunking for large documents

- Text Processing

Text chunking
Content extraction
Metadata handling
Cache management

- Security Measures

API key validation
Rate limiting
File size restrictions
Input sanitization

- Testing
Run the test suite:
'pytest tests/'
Test files include:

- Unit tests
Integration tests
Security tests
Performance tests

- -Logging
Logs are stored in the logs directory with different levels:

DEBUG: Detailed debugging information
INFO: General operational information
WARNING: Warning messages
ERROR: Error information

- Error Handling
The application includes comprehensive error handling for:

File upload errors
Processing errors
API errors
Authentication errors
Rate limiting errors

Frontend Features

PDF file upload interface
Interactive chat interface
Real-time responses
Document information display
Chat history management

Performance
The application implements several performance optimizations:

Text chunking for large documents
Response caching
Asynchronous operations
Rate limiting
Resource management

- Contributing

Fork the repository
Create your feature branch
Commit your changes
Push to the branch
Create a Pull Request

- License
MIT License
```
