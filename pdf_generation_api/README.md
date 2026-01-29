# PDF Generation API

A comprehensive PDF generation, conversion, and manipulation service built with FastAPI. This API provides advanced capabilities for creating, editing, merging, splitting, and converting PDF documents.

## 🚀 Features

### PDF Generation
- **Text to PDF**: Convert plain text content to formatted PDFs
- **HTML to PDF**: Convert HTML content to PDF documents
- **Advanced Formatting**: Custom page sizes, orientations, margins, fonts
- **Watermarking**: Add text watermarks to generated PDFs
- **Password Protection**: Secure PDFs with password encryption

### PDF Manipulation
- **Merge PDFs**: Combine multiple PDFs into a single document
- **Split PDFs**: Split PDFs into multiple files based on page ranges
- **Compress PDFs**: Reduce file size with quality controls
- **Metadata Management**: Read and update PDF metadata

### PDF Conversion
- **Format Conversion**: Convert PDFs to HTML, TXT, XML, CSV
- **Async Processing**: Background conversion jobs with status tracking
- **Batch Operations**: Process multiple files simultaneously

### File Management
- **Upload Support**: Upload existing PDFs for processing
- **Download Management**: Secure file download endpoints
- **Storage Tracking**: Monitor file usage and statistics

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **Data Validation**: Pydantic models
- **File Handling**: UploadFile, FileResponse
- **Background Tasks**: Asyncio for long-running operations

## 📋 API Endpoints

### PDF Generation

#### Generate PDF from Text
```http
POST /api/pdf/generate
Content-Type: application/json

{
  "content": "Your PDF content here...",
  "title": "My Document",
  "author": "John Doe",
  "page_size": "A4",
  "orientation": "portrait",
  "margin_top": 20.0,
  "margin_bottom": 20.0,
  "margin_left": 20.0,
  "margin_right": 20.0,
  "font_size": 12,
  "font_family": "Arial",
  "header_text": "Document Header",
  "footer_text": "Page {page}",
  "watermark_text": "CONFIDENTIAL",
  "password": "optional_password"
}
```

#### Generate PDF from HTML
```http
POST /api/pdf/generate-from-html
Content-Type: multipart/form-data

html_content: "<h1>Hello World</h1><p>This is a PDF generated from HTML.</p>"
title: "HTML to PDF"
page_size: "A4"
orientation: "portrait"
```

#### Upload Existing PDF
```http
POST /api/pdf/upload
Content-Type: multipart/form-data

file: [PDF file]
```

### PDF Manipulation

#### Merge Multiple PDFs
```http
POST /api/pdf/merge
Content-Type: application/json

{
  "pdf_files": ["pdf_id_1", "pdf_id_2", "pdf_id_3"],
  "output_filename": "merged_document.pdf",
  "password": "optional_password"
}
```

#### Split PDF
```http
POST /api/pdf/split
Content-Type: application/json

{
  "pdf_file": "pdf_id",
  "page_ranges": ["1-5", "6-10", "11-15"],
  "output_prefix": "document_part"
}
```

#### Compress PDF
```http
POST /api/pdf/compress/{pdf_id}
Content-Type: application/json

quality: "medium"  # low, medium, high
```

### PDF Conversion

#### Convert PDF to Other Format
```http
POST /api/pdf/convert/{pdf_id}
Content-Type: application/json

{
  "output_format": "html",  # html, txt, xml, csv
  "output_filename": "converted_document.html"
}
```

#### Get Conversion Status
```http
GET /api/pdf/convert-status/{conversion_id}
```

### Metadata Management

#### Get PDF Metadata
```http
GET /api/pdf/metadata/{pdf_id}
```

#### Update PDF Metadata
```http
PUT /api/pdf/metadata/{pdf_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "author": "New Author",
  "subject": "Updated Subject",
  "keywords": "keyword1, keyword2"
}
```

### Utility Endpoints

#### List All PDFs
```http
GET /api/pdf/list?limit=50&offset=0
```

#### Delete PDF
```http
DELETE /api/pdf/{pdf_id}
```

#### Download PDF
```http
GET /api/pdf/download/{pdf_id}
```

#### Get Statistics
```http
GET /api/pdf/stats
```

## 📊 Data Models

### PDFGenerationRequest
```python
class PDFGenerationRequest(BaseModel):
    content: str
    title: Optional[str] = "Generated PDF"
    author: Optional[str] = "PDF Generator"
    subject: Optional[str] = None
    keywords: Optional[str] = None
    page_size: Optional[str] = "A4"
    orientation: Optional[str] = "portrait"
    margin_top: Optional[float] = 20.0
    margin_bottom: Optional[float] = 20.0
    margin_left: Optional[float] = 20.0
    margin_right: Optional[float] = 20.0
    font_size: Optional[int] = 12
    font_family: Optional[str] = "Arial"
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    watermark_text: Optional[str] = None
    password: Optional[str] = None
```

### PDFMergeRequest
```python
class PDFMergeRequest(BaseModel):
    pdf_files: List[str]
    output_filename: Optional[str] = None
    password: Optional[str] = None
```

### PDFSplitRequest
```python
class PDFSplitRequest(BaseModel):
    pdf_file: str
    page_ranges: List[str]
    output_prefix: Optional[str] = "split"
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
PDF_STORAGE_PATH=./pdfs
MAX_FILE_SIZE=50MB
ALLOWED_FORMATS=pdf,html,txt
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Generate PDF from text
pdf_request = {
    "content": "This is a sample PDF document generated from text.",
    "title": "Sample Document",
    "author": "API User",
    "page_size": "A4",
    "orientation": "portrait"
}

response = requests.post(
    "http://localhost:8000/api/pdf/generate",
    json=pdf_request
)

if response.status_code == 200:
    result = response.json()
    pdf_id = result["pdf_id"]
    print(f"PDF generated with ID: {pdf_id}")
    
    # Download the PDF
    download_response = requests.get(f"http://localhost:8000/api/pdf/download/{pdf_id}")
    print(f"Download URL: {result['pdf_info']['download_url']}")

# Merge PDFs
merge_request = {
    "pdf_files": [pdf_id],
    "output_filename": "merged_document.pdf"
}

merge_response = requests.post(
    "http://localhost:8000/api/pdf/merge",
    json=merge_request
)

print(f"Merge result: {merge_response.json()}")
```

### JavaScript Client
```javascript
// Generate PDF from text
const pdfRequest = {
    content: "This is a sample PDF document generated from text.",
    title: "Sample Document",
    author: "API User",
    page_size: "A4",
    orientation: "portrait"
};

fetch('http://localhost:8000/api/pdf/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(pdfRequest)
})
.then(response => response.json())
.then(data => {
    console.log('PDF generated:', data);
    const pdfId = data.pdf_id;
    
    // Download PDF
    window.open(`http://localhost:8000/api/pdf/download/${pdfId}`);
})
.catch(error => console.error('Error:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# Storage Configuration
PDF_STORAGE_PATH=./pdfs
MAX_FILE_SIZE=50MB
TEMP_DIR=./temp

# Processing Configuration
MAX_CONVERSION_JOBS=10
CONVERSION_TIMEOUT=300
COMPRESSION_QUALITY=medium

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
API_KEY_REQUIRED=false
```

### Page Sizes
- **A4**: 210 × 297 mm (default)
- **A3**: 297 × 420 mm
- **Letter**: 8.5 × 11 inches
- **Legal**: 8.5 × 14 inches

### Orientations
- **portrait**: Vertical orientation (default)
- **landscape**: Horizontal orientation

### Compression Quality
- **low**: Maximum compression (30% of original size)
- **medium**: Balanced compression (60% of original size)
- **high**: High quality (80% of original size)

## 📈 Use Cases

### Document Generation
- **Invoices**: Generate invoices from template data
- **Reports**: Create business reports with charts and tables
- **Certificates**: Generate certificates with dynamic content
- **Contracts**: Create legal documents with templates

### Document Processing
- **Batch Processing**: Process multiple documents simultaneously
- **Format Conversion**: Convert documents between different formats
- **Content Extraction**: Extract text and metadata from PDFs
- **Document Optimization**: Reduce file sizes for web distribution

### Integration Examples
- **Web Applications**: Generate PDFs on-demand for users
- **Mobile Apps**: Create and share documents from mobile devices
- **Enterprise Systems**: Integrate with existing document workflows
- **E-commerce**: Generate invoices, receipts, and shipping labels

## 🛡️ Security Features

### File Security
- **File Type Validation**: Only PDF files are accepted
- **Size Limits**: Configurable maximum file sizes
- **Password Protection**: Optional PDF encryption
- **Secure Downloads**: Authenticated file access

### Data Protection
- **Temporary Storage**: Files are cleaned up after processing
- **Access Control**: API endpoints can be protected with authentication
- **Audit Logging**: Track all PDF operations
- **CORS Support**: Configure allowed origins for web integration

## 📊 Monitoring

### Statistics
- **Total PDFs**: Track number of generated documents
- **Storage Usage**: Monitor disk space consumption
- **Processing Jobs**: Track conversion and manipulation jobs
- **Performance Metrics**: Monitor API response times

### Health Checks
```http
GET /health
```

Returns API health status and timestamp.

## 🔗 Related APIs

- **Image Storage API**: For handling images in PDFs
- **Email Service API**: For sending generated PDFs via email
- **File Compression API**: For additional compression options
- **Data Validation API**: For validating PDF content

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API. In production, integrate with actual PDF libraries like:
- **ReportLab**: For PDF generation
- **WeasyPrint**: For HTML to PDF conversion
- **PyPDF2**: For PDF manipulation
- **pdfkit**: For PDF conversion utilities
