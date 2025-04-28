import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pdfplumber

from models.document import TableInfo
from core.document.processor import PDFProcessor
from utils.imports import HAS_PANDAS, pandas

class DataExtractor:
    """
    Handles extraction of structured data from PDF documents,
    such as tables, forms, and other structured content.
    """
    
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = Path(base_dir)
        self.extracted_dir = self.base_dir / "extracted"
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_processor = PDFProcessor(base_dir)
    
    def extract_text(self, document_id: str, pages: Optional[str] = None) -> str:
        """
        Extract text from a document, optionally from specific pages.
        
        Args:
            document_id: ID of the document
            pages: Optional string specifying pages to extract from (e.g., "1,3,5-7")
            
        Returns:
            Extracted text
        """
        # Get document metadata
        doc_metadata = self.pdf_processor.get_document(document_id)
        if not doc_metadata:
            raise ValueError(f"Document not found: {document_id}")
        
        # If text has already been extracted, return it
        if doc_metadata.text_path:
            # If no specific pages requested, return all text
            if not pages:
                return self.pdf_processor.get_document_text(document_id) or ""
        
        # Parse page specification
        page_numbers = self._parse_page_spec(pages, doc_metadata.page_count) if pages else None
        
        # If no specific pages requested, return all text
        if not page_numbers:
            return self.pdf_processor.get_document_text(document_id) or ""
        
        # Extract text from specific pages
        file_path = Path(doc_metadata.path)
        if not file_path.exists():
            raise ValueError(f"PDF file not found: {file_path}")
        
        extracted_text = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num in page_numbers:
                if 0 <= page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                    extracted_text.append(f"--- Page {page_num + 1} ---\n{text}")
        
        return "\n\n".join(extracted_text)
    
    def extract_tables(
        self, 
        document_id: str, 
        pages: Optional[str] = None,
        output_format: str = "json"
    ) -> Union[List[Dict[str, Any]], str, Path]:
        """
        Extract tables from a document, optionally from specific pages.
        
        Args:
            document_id: ID of the document
            pages: Optional string specifying pages to extract from (e.g., "1,3,5-7")
            output_format: Format to return tables in ("json", "csv", "excel")
            
        Returns:
            Extracted tables in the specified format
        """
        # Get document metadata
        doc_metadata = self.pdf_processor.get_document(document_id)
        if not doc_metadata:
            raise ValueError(f"Document not found: {document_id}")
        
        # Parse page specification
        page_numbers = self._parse_page_spec(pages, doc_metadata.page_count) if pages else None
        
        # Extract tables
        file_path = Path(doc_metadata.path)
        if not file_path.exists():
            raise ValueError(f"PDF file not found: {file_path}")
        
        # Create directory for extracted tables
        doc_extract_dir = self.extracted_dir / document_id
        doc_extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract tables from the PDF
        tables_data = []
        table_infos = []
        
        with pdfplumber.open(file_path) as pdf:
            # If no specific pages requested, process all pages
            if not page_numbers:
                page_numbers = list(range(len(pdf.pages)))
            
            for page_idx in page_numbers:
                if 0 <= page_idx < len(pdf.pages):
                    page = pdf.pages[page_idx]
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        # Convert table to a list of dictionaries
                        if table and len(table) > 1:  # Ensure there's at least a header row and one data row
                            headers = [str(cell).strip() if cell else f"Column{i+1}" for i, cell in enumerate(table[0])]
                            
                            # Create table info
                            table_info = TableInfo(
                                document_id=document_id,
                                page_number=page_idx + 1,
                                table_number=table_idx + 1,
                                rows=len(table),
                                columns=len(headers),
                                bbox=[0, 0, 0, 0]  # Placeholder
                            )
                            table_infos.append(table_info)
                            
                            # Process table rows
                            table_rows = []
                            for row_idx, row in enumerate(table[1:], 1):  # Skip header row
                                row_dict = {}
                                for col_idx, cell in enumerate(row):
                                    if col_idx < len(headers):
                                        header = headers[col_idx]
                                        row_dict[header] = cell.strip() if cell else ""
                                
                                table_rows.append(row_dict)
                            
                            # Add table to results
                            tables_data.append({
                                "page": page_idx + 1,
                                "table": table_idx + 1,
                                "headers": headers,
                                "rows": table_rows
                            })
        
        # Save table information
        tables_dict = [table.dict() for table in table_infos]
        # Convert datetime objects to strings
        tables_dict = self.pdf_processor._convert_datetime_to_str(tables_dict)
        with open(doc_extract_dir / "tables_info.json", 'w') as f:
            json.dump(tables_dict, f)
        
        # Return tables in the requested format
        if output_format == "json":
            # Return JSON data directly
            return tables_data
        
        elif output_format == "csv":
            # Convert to CSV
            csv_file = doc_extract_dir / "tables.csv"
            
            with open(csv_file, 'w', newline='') as f:
                for table_data in tables_data:
                    writer = csv.DictWriter(f, fieldnames=table_data["headers"])
                    f.write(f"Page {table_data['page']}, Table {table_data['table']}\n")
                    writer.writeheader()
                    writer.writerows(table_data["rows"])
                    f.write("\n\n")
            
            return csv_file
        
        elif output_format == "excel":
            # Convert to Excel
            excel_file = doc_extract_dir / "tables.xlsx"
            
            if not HAS_PANDAS:
                raise ImportError("pandas is required for Excel output. Please install pandas: pip install pandas")
            
            with pandas.ExcelWriter(excel_file) as writer:
                for table_data in tables_data:
                    df = pandas.DataFrame(table_data["rows"])
                    sheet_name = f"P{table_data['page']}_T{table_data['table']}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return excel_file
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def extract_form_fields(self, document_id: str) -> Dict[str, Any]:
        """
        Extract form fields from a PDF document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary of form field names and values
        """
        # Get document metadata
        doc_metadata = self.pdf_processor.get_document(document_id)
        if not doc_metadata:
            raise ValueError(f"Document not found: {document_id}")
        
        # Extract form fields
        file_path = Path(doc_metadata.path)
        if not file_path.exists():
            raise ValueError(f"PDF file not found: {file_path}")
        
        # This is a simplified implementation
        # pdfplumber doesn't directly support form field extraction
        # For a real implementation, you might use PyPDF2 or another library
        
        form_fields = {}
        
        # Create directory for extracted form data
        doc_extract_dir = self.extracted_dir / document_id
        doc_extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Save form field data
        with open(doc_extract_dir / "form_fields.json", 'w') as f:
            json.dump(form_fields, f)
        
        return form_fields
    
    def _parse_page_spec(self, page_spec: str, max_pages: int) -> List[int]:
        """
        Parse a page specification string into a list of page indices.
        
        Args:
            page_spec: String specifying pages (e.g., "1,3,5-7")
            max_pages: Maximum number of pages in the document
            
        Returns:
            List of zero-based page indices
        """
        if not page_spec:
            return list(range(max_pages))
        
        page_indices = []
        
        # Split by comma
        parts = page_spec.split(',')
        
        for part in parts:
            part = part.strip()
            
            # Handle page ranges (e.g., "5-7")
            if '-' in part:
                start, end = part.split('-')
                try:
                    start_idx = int(start.strip()) - 1  # Convert to 0-based index
                    end_idx = int(end.strip()) - 1
                    
                    # Validate range
                    if 0 <= start_idx <= end_idx < max_pages:
                        page_indices.extend(range(start_idx, end_idx + 1))
                except ValueError:
                    # Skip invalid ranges
                    continue
            
            # Handle single pages
            else:
                try:
                    page_idx = int(part) - 1  # Convert to 0-based index
                    
                    # Validate page number
                    if 0 <= page_idx < max_pages:
                        page_indices.append(page_idx)
                except ValueError:
                    # Skip invalid page numbers
                    continue
        
        # Remove duplicates and sort
        return sorted(set(page_indices))
