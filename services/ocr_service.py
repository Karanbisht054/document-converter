import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import os

class OCRService:
    def __init__(self):
        # Set Tesseract path for Windows
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def extract_text_from_image(self, image_path):
        try:
            # Open image and extract text
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image, lang='eng+hin')  # English + Hindi
            return extracted_text.strip()
        except Exception as e:
            print(f"OCR from image error: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            extracted_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # First try to extract text directly
                text = page.get_text()
                if text.strip():
                    extracted_text += text + "\n"
                else:
                    # If no text, use OCR on page image
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("ppm")
                    
                    # Save temporary image
                    temp_img_path = f"temp_page_{page_num}.png"
                    pix.save(temp_img_path)
                    
                    # Perform OCR
                    ocr_text = self.extract_text_from_image(temp_img_path)
                    extracted_text += ocr_text + "\n"
                    
                    # Clean up temp file
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
            
            doc.close()
            return extracted_text.strip()
        except Exception as e:
            print(f"OCR from PDF error: {e}")
            return ""