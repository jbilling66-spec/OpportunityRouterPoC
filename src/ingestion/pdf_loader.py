"""Source-agnostic ingestion. Manual PDF upload is the first adapter; the pipeline only
ever sees `document_text`, so email intake / a drive watcher can plug in later untouched.

PDF reality: some are clean digital text, some are scanned (need OCR), some are 200-page
monsters where the scope is buried. This is the unglamorous-but-hard part worth hardening.
This is a pragmatic baseline — native text first, OCR fallback flagged.
"""
from __future__ import annotations
from pathlib import Path

def pdf_to_text(path: str | Path) -> str:
    """Extract text from a PDF. Tries native text; flags when OCR is likely needed."""
    try:
        import pdfplumber  # pip install pdfplumber
    except ImportError as e:
        raise RuntimeError("pdfplumber not installed; see requirements.txt") from e

    pages = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()

    if len(text) < 200:
        # Likely a scanned/image PDF. Hook OCR here (e.g. pytesseract on rasterized pages).
        # [FILL IN OCR PATH] — left as a clear extension point.
        return text + "\n[INGESTION NOTE: little native text found; OCR likely required]"
    return text
