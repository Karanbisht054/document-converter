from pdf2image import convert_from_path
from PIL import Image
import os
import uuid

class ImageConverter:
    def pdf_to_images(self, pdf_path, output_folder, dpi=200):
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=dpi)
            
            output_paths = []
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for i, image in enumerate(images):
                output_filename = f"{base_name}_page_{i+1}_{uuid.uuid4().hex[:8]}.jpg"
                output_path = os.path.join(output_folder, output_filename)
                image.save(output_path, 'JPEG', quality=95)
                output_paths.append(output_path)
            
            return output_paths
        except Exception as e:
            print(f"PDF to images conversion error: {e}")
            return None
    
    def images_to_pdf(self, image_paths, output_folder):
        try:
            if not image_paths:
                return None
            
            # Open all images
            images = []
            for img_path in image_paths:
                img = Image.open(img_path)
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            # Generate output filename
            output_filename = f"merged_images_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            # Save as PDF
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            
            return output_path
        except Exception as e:
            print(f"Images to PDF conversion error: {e}")
            return None