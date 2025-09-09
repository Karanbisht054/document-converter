from pdf2docx import Converter
import os
import uuid

class PDFConverter:
    def pdf_to_docx(self, pdf_path, output_folder):
        try:
            # Generate unique output filename
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_filename = f"{base_name}_{uuid.uuid4()}.docx"
            output_path = os.path.join(output_folder, output_filename)
            
            # Convert PDF to DOCX
            cv = Converter(pdf_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            
            return output_path
        except Exception as e:
            print(f"PDF to DOCX conversion error: {e}")
            return None