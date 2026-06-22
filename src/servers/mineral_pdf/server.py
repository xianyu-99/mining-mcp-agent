from fastmcp import FastMCP
import logging
import requests
import tempfile
import pdfplumber
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("mineral-pdf")

@mcp.tool()
def extract_resources(pdf_url: str) -> str:
    """
    Extract NI 43-101 Indicated/Inferred resources from a PDF report.
    
    Args:
        pdf_url: The URL of the NI 43-101 PDF report.
    """
    logger.info(f"Extracting resources from {pdf_url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(pdf_url, stream=True, timeout=30, headers=headers)
        resp.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in resp.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp_path = tmp.name
            
        snippets = []
        with pdfplumber.open(tmp_path) as pdf:
            # Only scan first 50 pages to save time and token limits, usually resources are summarized early
            for i, page in enumerate(pdf.pages[:50]):
                text = page.extract_text()
                if text:
                    text_lower = text.lower()
                    if "indicated" in text_lower or "inferred" in text_lower:
                        snippets.append(f"--- Page {i+1} ---\n{text}")
        
        os.remove(tmp_path)
        
        if not snippets:
            return "No Indicated/Inferred resource data found in the first 50 pages of the PDF."
            
        # Truncate to avoid context limit issues
        full_text = "\n\n".join(snippets)
        return full_text[:4000] + "\n...(truncated)" if len(full_text) > 4000 else full_text
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return f"Failed to extract resources: {str(e)}"

if __name__ == "__main__":
    mcp.run()
