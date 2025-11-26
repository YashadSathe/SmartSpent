import base64
import os
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.schemas import ReceiptExtraction

class ReceiptScannerService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=api_key
        )
        
        self.structured_llm = self.llm.with_structured_output(ReceiptExtraction)

    def scan_receipt(self, image_bytes: bytes) -> ReceiptExtraction:
        # Encode image for the API
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        message = HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": "Extract the merchant or vendor name, transaction date, and list of purchased items/services with prices from this image (receipt or invoice). Ignore tax and totals."
                },
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                },
            ]
        )
        
        # Invoke Gemini
        return self.structured_llm.invoke([message])