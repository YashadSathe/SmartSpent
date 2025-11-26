import os
import json
import base64
import fitz  # PyMuPDF
import google.generativeai as genai
from app.schemas.schemas import ReceiptExtraction

class ReceiptScannerService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("CRITICAL: GOOGLE_API_KEY not set")
            raise ValueError("GOOGLE_API_KEY not set")
            
        # 1. Configure Google SDK Directly (Bypassing LangChain)
        genai.configure(api_key=api_key)
        
        # 2. Use the model directly (No "langchain" wrapper to cause 404s)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _convert_pdf_to_image(self, file_bytes: bytes) -> bytes:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            return pix.tobytes("png")
        except Exception as e:
            print(f"PDF Conversion Error: {e}")
            raise ValueError("Failed to convert PDF to image")

    def scan_receipt(self, file_bytes: bytes) -> ReceiptExtraction:
        try:
            # 1. Prepare Image
            is_pdf = file_bytes.startswith(b"%PDF")
            if is_pdf:
                print("📄 Processing PDF Invoice...")
                image_data = self._convert_pdf_to_image(file_bytes)
                mime_type = "image/png"
            else:
                print("📷 Processing Image Receipt...")
                image_data = file_bytes
                mime_type = "image/jpeg"

            # 2. Prompt for JSON
            prompt = """
            Analyze this receipt/invoice. Extract the following data in valid JSON format:
            {
                "merchant_name": "Store Name",
                "date": "YYYY-MM-DD",
                "items": [
                    {"item_name": "Item 1", "amount": 10.50}
                ]
            }
            Rules:
            - Ignore tax and subtotals.
            - If date is missing, return null.
            - Return ONLY the JSON object. No markdown.
            """

            # 3. Call Gemini
            response = self.model.generate_content([
                {'mime_type': mime_type, 'data': image_data},
                prompt
            ])

            # 4. Clean Response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[:-3]

            # 5. Validate
            data = json.loads(text)
            return ReceiptExtraction(**data)

        except Exception as e:
            print(f"Scanning Failed: {str(e)}")
            raise ValueError(f"AI Processing Failed: {str(e)}")