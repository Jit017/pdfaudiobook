"""
PDF Reader module for extracting clean text from PDF documents.

Handles PDF text extraction, cleaning, and preprocessing for TTS conversion.
Uses PyMuPDF (fitz) for robust PDF text extraction.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, List, Dict, Any

from .utils import setup_logging, timing_decorator, clean_text, log_event

# Module-level logger
logger = setup_logging(__name__)


class PDFReader:
    """
    Handles PDF text extraction and cleaning.
    
    Extracts text from PDF files while handling common issues like
    headers, footers, and formatting artifacts.
    """
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.current_pdf = None
        self.metadata = {}
    
    @timing_decorator
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a single string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        try:
            self.current_pdf = fitz.open(pdf_path)
            self.metadata = self._extract_metadata()
            
            self.logger.info(f"Processing PDF: {pdf_path.name}")
            self.logger.info(f"Pages: {len(self.current_pdf)}")
            
            all_text = ""
            for page_num in range(len(self.current_pdf)):
                page_text = self._extract_page_text(page_num)
                if page_text.strip():  # Only add non-empty pages
                    all_text += page_text + "\n\n"
            
            # Clean the extracted text
            cleaned_text = self._clean_extracted_text(all_text)
            
            self.logger.info(f"Extracted {len(cleaned_text)} characters from {pdf_path.name}")
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
        finally:
            if self.current_pdf:
                self.current_pdf.close()
    
    def _extract_page_text(self, page_num: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Text from the page
        """
        try:
            page = self.current_pdf[page_num]
            text = page.get_text()
            
            # Remove headers and footers (basic heuristic)
            text = self._remove_headers_footers(text, page_num)
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
            return ""
    
    def _remove_headers_footers(self, text: str, page_num: int) -> str:
        """
        Remove common headers and footers from page text.
        
        Args:
            text: Raw page text
            page_num: Page number for context
            
        Returns:
            Text with headers/footers removed
        """
        lines = text.split('\n')
        
        # Remove likely header (first few lines if they're short)
        if len(lines) > 3:
            if len(lines[0]) < 50 and (page_num > 0):  # Skip title page
                lines = lines[1:]
        
        # Remove likely footer (last few lines if they contain page numbers)
        if len(lines) > 3:
            last_line = lines[-1].strip()
            if (len(last_line) < 20 and 
                (last_line.isdigit() or 
                 any(word in last_line.lower() for word in ['page', 'chapter']))):
                lines = lines[:-1]
        
        return '\n'.join(lines)
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text ready for processing
        """
        # Use the utility function for basic cleaning
        text = clean_text(text)
        
        # Additional PDF-specific cleaning
        # Remove page breaks and excessive newlines
        text = text.replace('\n\n\n', '\n\n')
        text = text.replace('\n \n', '\n\n')
        
        # Fix common PDF extraction issues
        text = text.replace('- ', '')  # Remove hyphenation artifacts
        text = text.replace('•', '')   # Remove bullet points
        
        return text.strip()
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the PDF.
        
        Returns:
            Dictionary containing PDF metadata
        """
        if not self.current_pdf:
            return {}
        
        metadata = self.current_pdf.metadata
        return {
            'title': metadata.get('title', 'Unknown'),
            'author': metadata.get('author', 'Unknown'),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(self.current_pdf)
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the last processed PDF.
        
        Returns:
            Dictionary containing PDF metadata
        """
        return self.metadata.copy()
    
    def extract_text_by_pages(self, pdf_path: Path) -> List[str]:
        """
        Extract text from PDF, returning a list of pages.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text strings, one per page
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            self.current_pdf = fitz.open(pdf_path)
            self.metadata = self._extract_metadata()
            
            pages = []
            for page_num in range(len(self.current_pdf)):
                page_text = self._extract_page_text(page_num)
                cleaned_text = clean_text(page_text)
                if cleaned_text.strip():
                    pages.append(cleaned_text)
            
            self.logger.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
            return pages
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
        finally:
            if self.current_pdf:
                self.current_pdf.close()
    
    @staticmethod
    def validate_pdf(pdf_path: Path) -> bool:
        """
        Validate that a file is a readable PDF.
        
        Args:
            pdf_path: Path to check
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            if not pdf_path.exists() or not pdf_path.suffix.lower() == '.pdf':
                return False
            
            # Try to open the PDF
            doc = fitz.open(pdf_path)
            is_valid = len(doc) > 0  # Has at least one page
            doc.close()
            return is_valid
            
        except Exception:
            return False
    
    def get_text_sample(self, pdf_path: Path, max_chars: int = 500) -> str:
        """
        Get a sample of text from the beginning of the PDF.
        
        Args:
            pdf_path: Path to the PDF file
            max_chars: Maximum characters to return
            
        Returns:
            Sample text from the beginning of the PDF
        """
        try:
            full_text = self.extract_text(pdf_path)
            if len(full_text) <= max_chars:
                return full_text
            
            # Find a good breaking point (end of sentence)
            sample = full_text[:max_chars]
            last_period = sample.rfind('.')
            if last_period > max_chars * 0.8:  # If period is reasonably close
                sample = sample[:last_period + 1]
            
            return sample + "..."
            
        except Exception as e:
            return f"Error reading PDF: {e}"


# Main API function requested by user
@timing_decorator
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract clean text from a PDF file.
    
    This is the main API function for PDF text extraction. It handles
    PDF loading, text extraction, cleaning, and error handling.
    
    Args:
        pdf_path: Path to the PDF file as string
        
    Returns:
        Cleaned text content from the PDF
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If file is not a valid PDF
        Exception: For other PDF processing errors
        
    Example:
        >>> text = extract_text_from_pdf("document.pdf")
        >>> print(f"Extracted {len(text)} characters")
    """
    log_event(f"Starting PDF text extraction: {pdf_path}")
    
    pdf_path_obj = Path(pdf_path)
    
    # Validate input
    if not pdf_path_obj.exists():
        error_msg = f"PDF file not found: {pdf_path}"
        log_event(error_msg)
        raise FileNotFoundError(error_msg)
    
    if not pdf_path_obj.suffix.lower() == '.pdf':
        error_msg = f"File is not a PDF: {pdf_path}"
        log_event(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Use the PDFReader class for actual extraction
        reader = PDFReader()
        text = reader.extract_text(pdf_path_obj)
        
        log_event(f"Successfully extracted {len(text)} characters from {pdf_path_obj.name}")
        return text
        
    except Exception as e:
        error_msg = f"Error extracting text from PDF {pdf_path}: {e}"
        log_event(error_msg)
        raise 