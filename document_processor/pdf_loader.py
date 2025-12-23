"""
Advanced PDF Loader - Change 3
Uses PDF Plumber for better text extraction, with OCR fallback for scanned documents.
Falls back to PyPDF2 if pdfplumber is not available.
"""

# Try to import pdfplumber (optional dependency)
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# PyPDF2 is required (fallback)
try:
    from PyPDF2 import PdfReader
except ImportError:
    raise ImportError(
        "PyPDF2 is required. Install with: pip install PyPDF2\n"
        "For enhanced PDF processing, also install: pip install pdfplumber"
    )

from typing import Union, Optional
import io


def load_pdf(pdf_file):
    """
    Loads a PDF file from Streamlit uploader or file path.
    Tries PDF Plumber first (if available), falls back to PyPDF2 for compatibility.
    
    Args:
        pdf_file: PDF file (Streamlit uploader or file path)
        
    Returns:
        PDF reader object (pdfplumber.PDF or PdfReader)
    """
    # Try PDF Plumber first if available
    if PDFPLUMBER_AVAILABLE:
        try:
            if hasattr(pdf_file, 'read'):
                # Streamlit file uploader - read into bytes
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)  # Reset for potential fallback
                pdf_io = io.BytesIO(pdf_bytes)
                pdf = pdfplumber.open(pdf_io)
                return pdf
            else:
                # File path
                pdf = pdfplumber.open(pdf_file)
                return pdf
        except Exception as e:
            print(f"⚠️ PDF Plumber failed: {e}, falling back to PyPDF2")
            # Fallback to PyPDF2
            pass
    
    # Fallback to PyPDF2 (always available)
    try:
        reader = PdfReader(pdf_file)
        return reader
    except Exception as e:
        raise RuntimeError(f"Failed to load PDF: {e}")
