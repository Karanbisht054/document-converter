import docx2pdf
import os
import uuid
import platform

class DOCXConverter:
    def docx_to_pdf(self, docx_path, output_folder):
        try:
            # Generate unique output filename
            base_name = os.path.splitext(os.path.basename(docx_path))[0]
            output_filename = f"{base_name}_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            # Convert DOCX to PDF
            if platform.system() == "Windows":
                docx2pdf.convert(docx_path, output_path)
            else:
                # For Linux/Mac, use alternative method
                import subprocess
                subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', output_folder, docx_path
                ])
                # Rename the output file
                original_name = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
                original_path = os.path.join(output_folder, original_name)
                if os.path.exists(original_path):
                    os.rename(original_path, output_path)
            
            return output_path
        except Exception as e:
            print(f"DOCX to PDF conversion error: {e}")
            return None