"""
Receipt Capture Module

Processes receipt images using OCR and extracts key expense details.
Enhanced with custom OCR configuration and improved regex patterns.
"""

import re
from typing import Dict
from PIL import Image
import pytesseract


def process_receipt(image_path: str) -> Dict[str, str]:
    """
    Process a receipt image to extract key expense details.

    This function uses Tesseract OCR with a custom configuration to extract
    text from a receipt image. It then applies regex patterns to extract the
    amount, date, and a brief description. The function also heuristically
    determines the expense category based on keywords in the extracted text.
    """
    try:
        # Custom OCR configuration: PSM 6 (assumes a uniform block of text)
        custom_config = r'--psm 6'
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config=custom_config)
        result: Dict[str, str] = {}

        # Define regex patterns for extracting the amount
        amount_patterns = [
            r'(?:Total|Amount)[^\d]*(\d{1,3}(?:[,\d{3}]*\.\d{2}))',
            r'\$\s*(\d{1,3}(?:[,\d{3}]*\.\d{2}))'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(",", ""))
                    result["amount"] = f"₹{amount:,.2f}"
                    break
                except ValueError:
                    continue

        # Extract date using regex for formats: YYYY-MM-DD or DD-MM-YYYY
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(date_pattern, text)
        if not match:
            date_pattern_alt = r'(\d{2}-\d{2}-\d{4})'
            match = re.search(date_pattern_alt, text)
        if match:
            result["date"] = match.group(1)

        # Generate a description from the first few non-empty lines of text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            result["description"] = " ".join(lines[:3])
            lower_text = text.lower()
            if any(keyword in lower_text for keyword in ["restaurant", "cafe", "lunch", "dinner", "meal"]):
                result["category"] = "Food"
            elif any(keyword in lower_text for keyword in ["grocery", "supermarket", "mart"]):
                result["category"] = "Shopping"
            elif any(keyword in lower_text for keyword in ["uber", "taxi", "bus", "train", "transport"]):
                result["category"] = "Transport"
            else:
                result["category"] = "Other"
                
        return result
    except Exception as e:
        print("OCR error: Tesseract may not be installed or not in PATH. Error:", e)
        return {}
