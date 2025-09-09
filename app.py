from flask import Flask, request, render_template, send_file, jsonify, flash
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Import conversion modules
from services.pdf_converter import PDFConverter
from services.docx_converter import DOCXConverter
from services.image_converter import ImageConverter
from services.ocr_service import OCRService
from services.text_editor import TextEditor

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
TEMP_FOLDER = 'temp'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': ['pdf'],
    'docx': ['docx', 'doc'],
    'image': ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
}

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename, file_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

# PDF to DOCX conversion
@app.route('/convert/pdf-to-docx', methods=['POST'])
def pdf_to_docx():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        # Convert PDF to DOCX
        converter = PDFConverter()
        output_path = converter.pdf_to_docx(upload_path, CONVERTED_FOLDER)
        
        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DOCX to PDF conversion
@app.route('/convert/docx-to-pdf', methods=['POST'])
def docx_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename, 'docx'):
            return jsonify({'error': 'Invalid DOCX file'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        converter = DOCXConverter()
        output_path = converter.docx_to_pdf(upload_path, CONVERTED_FOLDER)
        
        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PDF to JPG conversion
@app.route('/convert/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        converter = ImageConverter()
        output_paths = converter.pdf_to_images(upload_path, CONVERTED_FOLDER)
        
        if output_paths:
            # Create ZIP file with all images
            import zipfile
            zip_filename = f"converted_images_{uuid.uuid4()}.zip"
            zip_path = os.path.join(CONVERTED_FOLDER, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for img_path in output_paths:
                    zip_file.write(img_path, os.path.basename(img_path))
            
            return send_file(zip_path, as_attachment=True)
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# JPG to PDF conversion
@app.route('/convert/jpg-to-pdf', methods=['POST'])
def jpg_to_pdf():
    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        valid_files = []
        for file in files:
            if file and allowed_file(file.filename, 'image'):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(upload_path)
                valid_files.append(upload_path)
        
        if not valid_files:
            return jsonify({'error': 'No valid image files'}), 400
        
        converter = ImageConverter()
        output_path = converter.images_to_pdf(valid_files, CONVERTED_FOLDER)
        
        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# OCR Service
@app.route('/ocr', methods=['POST'])
def perform_ocr():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file:
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        ocr_service = OCRService()
        
        # Check file type and perform OCR accordingly
        if allowed_file(file.filename, 'image'):
            extracted_text = ocr_service.extract_text_from_image(upload_path)
        elif allowed_file(file.filename, 'pdf'):
            extracted_text = ocr_service.extract_text_from_pdf(upload_path)
        else:
            return jsonify({'error': 'Unsupported file type for OCR'}), 400
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Text Editor
@app.route('/edit-text', methods=['POST'])
def edit_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        operation = data.get('operation', 'format')
        
        text_editor = TextEditor()
        
        if operation == 'format':
            formatted_text = text_editor.format_text(text)
            return jsonify({
                'success': True,
                'formatted_text': formatted_text
            })
        elif operation == 'to_docx':
            # Create DOCX file from text
            output_path = text_editor.text_to_docx(text, CONVERTED_FOLDER)
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Invalid operation'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
    # Add file validation in app.py
import magic

def validate_file_type(file_path, expected_type):
    file_type = magic.from_file(file_path, mime=True)
    return file_type.startswith(expected_type)
# Add automatic cleanup function
import schedule
import time
from datetime import datetime, timedelta

def cleanup_old_files():
    cutoff_time = datetime.now() - timedelta(hours=24)
    for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER, TEMP_FOLDER]:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.getctime(file_path) < cutoff_time.timestamp():
                os.remove(file_path)

# Schedule cleanup every hour
schedule.every().hour.do(cleanup_old_files)
    # If OCR fails, check Tesseract installation
import pytesseract
print(pytesseract.get_tesseract_version())

# For Windows, set correct path in services/ocr_service.py:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'