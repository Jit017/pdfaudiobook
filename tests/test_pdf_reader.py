"""
Tests for the PDF Reader module.
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from src.pdf_reader import PDFReader


class TestPDFReader:
    """Test cases for PDFReader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = PDFReader()
    
    def test_pdf_reader_initialization(self):
        """Test PDFReader initializes correctly."""
        assert self.reader is not None
        assert hasattr(self.reader, 'logger')
        assert self.reader.current_pdf is None
    
    def test_validate_pdf_nonexistent_file(self):
        """Test PDF validation with non-existent file."""
        fake_path = Path("nonexistent.pdf")
        assert not self.reader.validate_pdf(fake_path)
    
    def test_validate_pdf_wrong_extension(self):
        """Test PDF validation with wrong file extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            txt_path = Path(tmp.name)
            assert not self.reader.validate_pdf(txt_path)
    
    def test_extract_text_nonexistent_file(self):
        """Test text extraction raises error for non-existent file."""
        fake_path = Path("nonexistent.pdf")
        with pytest.raises(FileNotFoundError):
            self.reader.extract_text(fake_path)
    
    def test_extract_text_wrong_format(self):
        """Test text extraction raises error for non-PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            txt_path = Path(tmp.name)
            with pytest.raises(ValueError):
                self.reader.extract_text(txt_path)
    
    def test_get_metadata_empty(self):
        """Test metadata retrieval when no PDF is loaded."""
        metadata = self.reader.get_metadata()
        assert metadata == {}
    
    def test_clean_extracted_text(self):
        """Test text cleaning functionality."""
        raw_text = "This  is   a   test\n\n\nwith   extra   spaces\n \n"
        cleaned = self.reader._clean_extracted_text(raw_text)
        
        # Should remove excessive whitespace and newlines
        assert "   " not in cleaned
        assert "\n\n\n" not in cleaned
        assert cleaned.strip() == cleaned
    
    def test_remove_headers_footers(self):
        """Test header and footer removal."""
        text_with_header = "Chapter 1\nThis is the main content\nPage 5"
        
        # First page (shouldn't remove title)
        result = self.reader._remove_headers_footers(text_with_header, 0)
        assert "Chapter 1" in result
        
        # Later page (should remove short header and page number)
        result = self.reader._remove_headers_footers(text_with_header, 5)
        assert "This is the main content" in result
    
    def test_extract_text_by_pages_nonexistent(self):
        """Test page-by-page extraction with non-existent file."""
        fake_path = Path("nonexistent.pdf")
        with pytest.raises(FileNotFoundError):
            self.reader.extract_text_by_pages(fake_path)
    
    def test_get_text_sample_nonexistent(self):
        """Test text sample extraction with non-existent file."""
        fake_path = Path("nonexistent.pdf")
        sample = self.reader.get_text_sample(fake_path)
        assert "Error reading PDF" in sample
    
    @pytest.mark.integration
    def test_with_sample_pdf(self):
        """Integration test with a real PDF file (if available)."""
        # This test would run only if a sample PDF is available
        sample_pdf = Path("tests/sample.pdf")
        if sample_pdf.exists():
            text = self.reader.extract_text(sample_pdf)
            assert isinstance(text, str)
            assert len(text) > 0
            
            metadata = self.reader.get_metadata()
            assert isinstance(metadata, dict)
            assert 'page_count' in metadata
        else:
            pytest.skip("No sample PDF available for integration testing")


if __name__ == "__main__":
    pytest.main([__file__]) 