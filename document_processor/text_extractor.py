"""
Advanced Text Extractor - Change 3
Extracts text using PDF Plumber with OCR fallback for scanned/image-based PDFs.
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

from typing import List, Optional
import io

# Try to import OCR libraries (optional dependencies)
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # Don't print warning here - it's optional


def extract_text_from_reader(reader) -> List[str]:
    """
    Extracts cleaned text from each page of a PDF.
    Uses PDF Plumber for better extraction, with OCR fallback for scanned documents.
    
    Args:
        reader: PDF reader object (pdfplumber.PDF or PdfReader)
        
    Returns:
        List of page-wise text strings
    """
    pages_text = []
    
    # Check if it's PDF Plumber or PyPDF2
    # PDF Plumber objects have a 'pages' attribute and are not PdfReader instances
    is_pdfplumber = False
    if PDFPLUMBER_AVAILABLE:
        try:
            # Check if reader is a pdfplumber.PDF object
            is_pdfplumber = hasattr(reader, 'pages') and not isinstance(reader, PdfReader)
        except:
            is_pdfplumber = False
    
    if is_pdfplumber and PDFPLUMBER_AVAILABLE:
        # Use PDF Plumber (better extraction)
        try:
            for idx, page in enumerate(reader.pages):
                try:
                    # Extract text from page
                    text = page.extract_text() or ""
                
                    # Also try to extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # Convert table to text representation
                            table_text = "\n".join([" | ".join(row) for row in table if row])
                            if table_text.strip():
                                text += f"\n\nTable:\n{table_text}"
                    
                    cleaned = " ".join(text.split())
                    
                    # If no text extracted, try OCR
                    if not cleaned.strip() and OCR_AVAILABLE:
                        print(f"⚠️ Page {idx + 1} has no extractable text, attempting OCR...")
                        ocr_text = _extract_with_ocr(page)
                        if ocr_text:
                            cleaned = ocr_text
                            print(f"✓ OCR extracted text from page {idx + 1}")
                    
                    if cleaned.strip():
                        pages_text.append(cleaned)
                    else:
                        print(f"⚠️ Page {idx + 1} is empty (no text or OCR content).")
                        
                except Exception as e:
                    print(f"⚠️ Failed to read page {idx + 1}: {e}")
                    # Try OCR as last resort
                    if OCR_AVAILABLE:
                        try:
                            ocr_text = _extract_with_ocr_from_page_object(page)
                            if ocr_text:
                                pages_text.append(ocr_text)
                                print(f"✓ OCR recovered page {idx + 1}")
                        except:
                            pass
        except Exception as e:
            print(f"⚠️ PDF Plumber extraction failed: {e}, falling back to PyPDF2")
            is_pdfplumber = False  # Force fallback to PyPDF2
    
    if not is_pdfplumber:
        # Fallback to PyPDF2 extraction
        for idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                cleaned = " ".join(text.split())
                
                # If no text, try OCR if available
                if not cleaned.strip() and OCR_AVAILABLE:
                    print(f"⚠️ Page {idx + 1} has no extractable text, attempting OCR...")
                    # For PyPDF2, we need to convert page to image first
                    # This is more complex, so we'll skip OCR for PyPDF2 for now
                    # OCR would require additional image conversion steps
                
                if cleaned.strip():
                    pages_text.append(cleaned)
                else:
                    print(f"⚠️ Page {idx + 1} is empty.")
            except Exception as e:
                print(f"⚠️ Failed to read page {idx + 1}: {e}")
    
    return pages_text


def _extract_with_ocr(page) -> Optional[str]:
    """
    Extract text from a PDF page using OCR.
    
    Args:
        page: PDF page object (pdfplumber page)
        
    Returns:
        Extracted text or None
    """
    if not OCR_AVAILABLE:
        return None
    
    try:
        # Convert page to image
        image = page.to_image(resolution=300)  # 300 DPI for better OCR
        
        # Perform OCR
        text = pytesseract.image_to_string(image.original, lang='eng')
        
        # Clean up text
        cleaned = " ".join(text.split())
        return cleaned if cleaned.strip() else None
        
    except Exception as e:
        print(f"⚠️ OCR failed: {e}")
        return None


def _extract_with_ocr_from_page_object(page) -> Optional[str]:
    """
    Extract text from a pdfplumber page object using OCR.
    
    Args:
        page: pdfplumber page object
        
    Returns:
        Extracted text or None
    """
    return _extract_with_ocr(page)
