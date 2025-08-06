"""
Utilities for parsing PDF, DOCX, and EML files.
"""
import fitz  # PyMuPDF
import docx
import email
from bs4 import BeautifulSoup
from .logging_utils import get_logger

logger = get_logger("parser_utils")

def parse_pdf(file_path: str) -> str:
    """Parse PDF and return normalized text."""
    try:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}")
        return ""

def parse_docx(file_path: str) -> str:
    """Parse DOCX and return normalized text."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to parse DOCX: {e}")
        return ""

def parse_eml(file_path: str) -> str:
    """Parse EML and return normalized text."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            msg = email.message_from_file(f)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/plain':
                    body += part.get_payload(decode=True).decode(errors='ignore')
                elif ctype == 'text/html':
                    html = part.get_payload(decode=True).decode(errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    body += soup.get_text()
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode(errors='ignore')
                except Exception:
                    body = str(payload)
        return body.strip()
    except Exception as e:
        logger.error(f"Failed to parse EML: {e}")
        return ""