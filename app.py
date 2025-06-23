import os
import logging
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import shutil
from converters import (PDFToPNGConverter, PNGToJPGConverter, MP4ToMP3Converter, 
                      DOCXToPDFConverter, DOCToPDFConverter, TXTToPDFConverter,
                      EPUBToPDFConverter, JPGToPDFConverter, PDFToDOCXConverter,
                      XLSXToPDFConverter, PPTXToPDFConverter, PDFToTXTConverter,
                      XLSXToCSVConverter, CSVToXLSXConverter, CSVToPDFConverter,
                      HTMLToPDFConverter, PDFToHTMLConverter, MP3ToWAVConverter,
                      WAVToMP3Converter, MP4ToAVIConverter, AVIToMP4Converter,
                      WEBPToJPGConverter, BMPToPNGConverter, CompressPDFConverter,
                      JPGToWEBPConverter, JPGToPNGConverter, MKVToMP4Converter,
                      MP4ToWEBMConverter, OGGToMP3Converter, MergePDFsConverter,
                      MergeImagesConverter)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Ensure upload and converted directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# Allowed file extensions for each conversion type
ALLOWED_EXTENSIONS = {
    # Document conversions
    'pdf_to_docx': {'pdf'},
    'docx_to_pdf': {'docx'},
    'doc_to_pdf': {'doc'},
    'pptx_to_pdf': {'pptx'},
    'pdf_to_txt': {'pdf'},
    'txt_to_pdf': {'txt'},
    'xlsx_to_csv': {'xlsx', 'xls'},
    'csv_to_xlsx': {'csv'},
    'xlsx_to_pdf': {'xlsx', 'xls'},
    'csv_to_pdf': {'csv'},
    'html_to_pdf': {'html', 'htm'},
    'epub_to_pdf': {'epub'},
    'pdf_to_html': {'pdf'},
    
    # Image conversions
    'jpg_to_png': {'jpg', 'jpeg'},
    'png_to_jpg': {'png'},
    'webp_to_jpg': {'webp'},
    'jpg_to_webp': {'jpg', 'jpeg'},
    'image_to_pdf': {'jpg', 'jpeg', 'png', 'webp', 'bmp'},
    'pdf_to_png': {'pdf'},
    'bmp_to_png': {'bmp'},
    
    # Audio conversions
    'mp3_to_wav': {'mp3'},
    'wav_to_mp3': {'wav'},
    'mp4_to_mp3': {'mp4'},
    
    # Video conversions
    'mp4_to_avi': {'mp4'},
    'avi_to_mp4': {'avi'},
    'mkv_to_mp4': {'mkv'},
    'mp4_to_webm': {'mp4'},
    
    # Additional audio
    'ogg_to_mp3': {'ogg'},
    
    # Extras
    'compress_pdf': {'pdf'},
    'merge_pdfs': {'pdf'},
    'merge_images': {'jpg', 'jpeg', 'png', 'webp', 'bmp'}
}

# Initialize converters
converters = {
    # Document conversions
    'pdf_to_docx': PDFToDOCXConverter(),
    'docx_to_pdf': DOCXToPDFConverter(),
    'doc_to_pdf': DOCToPDFConverter(),
    'pptx_to_pdf': PPTXToPDFConverter(),
    'pdf_to_txt': PDFToTXTConverter(),
    'txt_to_pdf': TXTToPDFConverter(),
    'xlsx_to_csv': XLSXToCSVConverter(),
    'csv_to_xlsx': CSVToXLSXConverter(),
    'xlsx_to_pdf': XLSXToPDFConverter(),
    'csv_to_pdf': CSVToPDFConverter(),
    'html_to_pdf': HTMLToPDFConverter(),
    'epub_to_pdf': EPUBToPDFConverter(),
    'pdf_to_html': PDFToHTMLConverter(),
    
    # Image conversions
    'jpg_to_png': JPGToPNGConverter(),
    'png_to_jpg': PNGToJPGConverter(),
    'webp_to_jpg': WEBPToJPGConverter(),
    'jpg_to_webp': JPGToWEBPConverter(),
    'image_to_pdf': JPGToPDFConverter(),
    'pdf_to_png': PDFToPNGConverter(),
    'bmp_to_png': BMPToPNGConverter(),
    
    # Audio conversions
    'mp3_to_wav': MP3ToWAVConverter(),
    'wav_to_mp3': WAVToMP3Converter(),
    'mp4_to_mp3': MP4ToMP3Converter(),
    'ogg_to_mp3': OGGToMP3Converter(),
    
    # Video conversions
    'mp4_to_avi': MP4ToAVIConverter(),
    'avi_to_mp4': AVIToMP4Converter(),
    'mkv_to_mp4': MKVToMP4Converter(),
    'mp4_to_webm': MP4ToWEBMConverter(),
    
    # Extras
    'compress_pdf': CompressPDFConverter(),
    'merge_pdfs': MergePDFsConverter(),
    'merge_images': MergeImagesConverter()
}

def allowed_file(filename, conversion_type):
    """Check if file extension is allowed for the conversion type"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(conversion_type, set())

@app.route('/')
def index():
    """Home page with file upload form"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    """Handle file conversion"""
    try:
        conversion_type = request.form.get('conversion_type')
        
        # Special handling for multi-file operations
        if conversion_type == 'merge_pdfs':
            return handle_pdf_merge()
        elif conversion_type == 'merge_images':
            return handle_image_merge()
        
        # Regular single file conversion
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        # Validate inputs
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not conversion_type or conversion_type not in converters:
            flash('Invalid conversion type selected', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename, conversion_type):
            flash(f'Invalid file type for {conversion_type.replace("_", " ").title()} conversion', 'error')
            return redirect(url_for('index'))
        
        # Create temporary directories for this conversion
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            # Get converter and perform conversion
            converter = converters[conversion_type]
            output_path = converter.convert(input_path, temp_dir)
            
            if not output_path or not os.path.exists(output_path):
                flash('Conversion failed. Please try again.', 'error')
                return redirect(url_for('index'))
            
            # Send file to user
            download_name = os.path.basename(output_path)
            
            # Special handling for PDF to PNG (ZIP file)
            if conversion_type == 'pdf_to_png' and output_path.endswith('.zip'):
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                download_name = f"{base_name}_all_pages.zip"
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=download_name,
                mimetype=converter.output_mimetype
            )
            
        except Exception as e:
            logging.error(f"Conversion error: {str(e)}")
            flash(f'Conversion failed: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.warning(f"Failed to clean up temp directory: {str(e)}")
    
    except RequestEntityTooLarge:
        flash('File too large. Maximum size is 50MB.', 'error')
        return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

def handle_pdf_merge():
    """Handle PDF merge with multiple file uploads"""
    try:
        # Check if files were uploaded
        uploaded_files = request.files.getlist('files')
        
        if not uploaded_files or len(uploaded_files) < 2:
            flash('Please select at least 2 PDF files to merge', 'error')
            return redirect(url_for('index'))
        
        # Validate all files are PDFs
        pdf_files = []
        for file in uploaded_files:
            if file.filename == '':
                continue
            if not file.filename.lower().endswith('.pdf'):
                flash(f'All files must be PDF format. Invalid file: {file.filename}', 'error')
                return redirect(url_for('index'))
            pdf_files.append(file)
        
        if len(pdf_files) < 2:
            flash('Please select at least 2 valid PDF files to merge', 'error')
            return redirect(url_for('index'))
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save all uploaded PDFs
            input_paths = []
            for i, file in enumerate(pdf_files):
                filename = secure_filename(f"input_{i+1:02d}_{file.filename}")
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                input_paths.append(input_path)
            
            # Perform PDF merge
            converter = MergePDFsConverter()
            output_path = converter.convert(input_paths, temp_dir)
            
            if not output_path or not os.path.exists(output_path):
                flash('PDF merge failed. Please try again.', 'error')
                return redirect(url_for('index'))
            
            # Send merged PDF to user
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"merged_{len(pdf_files)}_pdfs.pdf",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            logging.error(f"PDF merge error: {str(e)}")
            flash(f'PDF merge failed: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.warning(f"Failed to clean up temp directory: {str(e)}")
    
    except Exception as e:
        logging.error(f"Unexpected error in PDF merge: {str(e)}")
        flash('An unexpected error occurred during PDF merge. Please try again.', 'error')
        return redirect(url_for('index'))

def handle_image_merge():
    """Handle image merge with multiple file uploads"""
    try:
        # Check if files were uploaded
        uploaded_files = request.files.getlist('files')
        
        if not uploaded_files or len(uploaded_files) < 2:
            flash('Please select at least 2 image files to merge', 'error')
            return redirect(url_for('index'))
        
        # Validate all files are images
        image_files = []
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            
            file_ext = os.path.splitext(file.filename.lower())[1]
            if file_ext not in allowed_extensions:
                flash(f'Invalid file type: {file.filename}. Only JPG, PNG, WEBP, BMP images are supported.', 'error')
                return redirect(url_for('index'))
            image_files.append(file)
        
        if len(image_files) < 2:
            flash('Please select at least 2 valid image files to merge', 'error')
            return redirect(url_for('index'))
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save all uploaded images
            input_paths = []
            for i, file in enumerate(image_files):
                filename = secure_filename(f"image_{i+1:02d}_{file.filename}")
                input_path = os.path.join(temp_dir, filename)
                file.save(input_path)
                input_paths.append(input_path)
            
            # Perform image merge
            converter = MergeImagesConverter()
            output_path = converter.convert(input_paths, temp_dir)
            
            if not output_path or not os.path.exists(output_path):
                flash('Image merge failed. Please try again.', 'error')
                return redirect(url_for('index'))
            
            # Send merged PDF to user
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"merged_{len(image_files)}_images.pdf",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            logging.error(f"Image merge error: {str(e)}")
            flash(f'Image merge failed: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.warning(f"Failed to clean up temp directory: {str(e)}")
    
    except Exception as e:
        logging.error(f"Unexpected error in image merge: {str(e)}")
        flash('An unexpected error occurred during image merge. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 50MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
