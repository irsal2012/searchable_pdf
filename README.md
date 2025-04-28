# Searchable PDF

A powerful Python library and API for processing, searching, and extracting data from PDF documents.

## Features

- **PDF Processing**: Extract text, metadata, and structure from PDF documents
- **Full-Text Search**: Search across all your PDF documents with advanced query capabilities
- **Table Extraction**: Automatically detect and extract tables from PDFs to CSV, Excel, or JSON
- **Content Analysis**: Generate summaries and extract named entities from document content
- **API & CLI**: Access functionality through a RESTful API or command-line interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/searchable-pdf.git
   cd searchable-pdf
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install spaCy language model (optional, for better entity extraction):
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

### API Server

Start the API server:

```
cd searchable_pdf
python main.py
```

The API will be available at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

### Command-Line Interface

The library includes a command-line interface for common operations:

```
python cli.py [command] [options]
```

Available commands:

- `upload`: Upload a PDF document to the library
- `list`: List documents in the library
- `get`: Get document metadata
- `delete`: Delete a document
- `search`: Search for documents
- `extract-text`: Extract text from a document
- `extract-tables`: Extract tables from a document
- `summarize`: Generate a summary of a document
- `entities`: Extract entities from a document
- `index`: Index documents for searching

Examples:

```
# Upload a PDF document
python cli.py upload path/to/document.pdf --collection research

# Search for documents
python cli.py search "climate change" --collection research

# Extract tables from a document
python cli.py extract-tables document_id --format excel --output tables.xlsx

# Generate a summary of a document
python cli.py summarize document_id --max-length 1000 --output summary.txt
```

## API Endpoints

The API provides the following endpoints:

- `POST /documents/upload`: Upload a PDF document
- `GET /documents`: List documents in the library
- `GET /documents/{document_id}`: Get document metadata
- `DELETE /documents/{document_id}`: Delete a document
- `POST /search`: Search for documents
- `GET /documents/{document_id}/extract/text`: Extract text from a document
- `GET /documents/{document_id}/extract/tables`: Extract tables from a document
- `GET /documents/{document_id}/analyze/summary`: Generate a summary of a document
- `GET /documents/{document_id}/analyze/entities`: Extract entities from a document

## Project Structure

```
searchable_pdf/
├── api/                  # API endpoints
├── core/                 # Core application logic
│   ├── document/         # Document processing
│   ├── search/           # Search functionality
│   ├── extraction/       # Data extraction
│   └── analytics/        # Content analysis
├── models/               # Data models
├── storage/              # Storage for documents and processed data
├── utils/                # Utility functions
├── config/               # Configuration
├── main.py               # API entry point
└── cli.py                # Command-line interface
```

## Use Cases

### Research Document Management

Organize and search through research papers, extract tables of data, and generate summaries to quickly understand content.

### Legal Document Analysis

Search across case documents for specific legal terms, extract entities (people, organizations, dates), and identify relevant sections.

### Financial Document Processing

Extract data from invoices and financial reports, convert tables to structured formats, and organize documents by collection.

### Academic Paper Analysis

Extract data tables from research papers, find connections between papers, and generate summaries of technical content.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing and data extraction
- [PyPDF2](https://github.com/py-pdf/pypdf) - PDF processing
- [Whoosh](https://github.com/mchaput/whoosh) - Full-text search
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [spaCy](https://spacy.io/) - Natural language processing
