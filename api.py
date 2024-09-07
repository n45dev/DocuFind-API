import re
import fitz
import os
import sqlite3
from flask import Flask, request, jsonify, send_file
from io import BytesIO
from flask_cors import CORS
import mysql.connector

api_key = os.environ.get('API_KEY')

def get_db_connection():
    # Create and return a new connection when needed
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),
        port=os.environ.get('MYSQL_PORT'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE')
    )

app = Flask(__name__)
CORS(app)

# Initialize the MySQL database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_files (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            uploaded_pdf LONGBLOB,
                            underlined_pdf LONGBLOB)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_images (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        page_number INT,
                        image LONGBLOB,
                        pdf_id INT,
                        FOREIGN KEY (pdf_id) REFERENCES pdf_files (id))''')
    conn.commit()
    cursor.close()
    conn.close()

def extract_numbers(pdf_path, pattern):
    numbers = []
    with open(pdf_path, 'rb') as file:
        reader = fitz.open(file)
        for page in reader:
            text = page.get_text("text")
            matches = re.findall(pattern, text)
            numbers.extend(matches)
    return numbers

def underline_numbers_in_pdf(original_pdf_path, output_pdf_path, numbers):
    original_pdf = fitz.open(original_pdf_path)
    for page_num in range(len(original_pdf)):
        page = original_pdf[page_num]
        for number in numbers:
            text_instances = page.search_for(number)
            for inst in text_instances:
                # Underline the number (draw box around it)
                page.draw_rect(inst, color=(0, 1, 0), width=1)
    original_pdf.save(output_pdf_path)
    original_pdf.close()

def convert_pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        images.append((page_num + 1, img_bytes))  # Store the page number and image bytes
    pdf_document.close()
    return images

# Save PDF and images to the database
def save_to_db(uploaded_pdf_bytes, underlined_pdf_bytes, images):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the PDFs
    cursor.execute("INSERT INTO pdf_files (uploaded_pdf, underlined_pdf) VALUES (%s, %s)",
                   (uploaded_pdf_bytes, underlined_pdf_bytes))
    pdf_id = cursor.lastrowid  # Get the generated pdf_id

    # Insert the images
    for page_number, image in images:
        cursor.execute("INSERT INTO pdf_images (page_number, image, pdf_id) VALUES (%s, %s, %s)",
                       (page_number, image, pdf_id))

    conn.commit()
    cursor.close()
    conn.close()

    return pdf_id  # Return the pdf_id

# Retrieve a PDF from the database
def get_pdf_from_db(pdf_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT underlined_pdf FROM pdf_files WHERE id = %s", (pdf_id,))
    pdf_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return pdf_data[0] if pdf_data else None

# Retrieve an image from the database
def get_image_from_db(pdf_id, page_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM pdf_images WHERE pdf_id = %s AND page_number = %s", (pdf_id, page_number))
    image_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return image_data[0] if image_data else None

# Retrive no of pdfs in the database
def get_pdf_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pdf_files")
    count = cursor.fetchone()
    cursor.close()
    conn.close()
    return count[0] if count else None

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    key = request.form.get('key')

    if key != api_key:
        return jsonify({"error": "Invalid key"}), 401

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read the uploaded PDF file
    uploaded_pdf_bytes = file.read()
    input_pdf_path = 'data/uploaded.pdf'

    # Save the uploaded file temporarily to extract text
    with open(input_pdf_path, 'wb') as f:
        f.write(uploaded_pdf_bytes)

    # Define patterns for Aadhaar, PAN, DL, and phone numbers
    aadhaar_pattern = r"\b\d{4} \d{4} \d{4}\b"
    pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    dl_pattern = r"^(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9]{2})[0-9]{7}$"
    phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'

    extracted_aadhaar_numbers = extract_numbers(input_pdf_path, aadhaar_pattern)
    extracted_pan_numbers = extract_numbers(input_pdf_path, pan_pattern)
    extracted_dl_numbers = extract_numbers(input_pdf_path, dl_pattern)
    extracted_phone_numbers = extract_numbers(input_pdf_path, phone_pattern)

    all_extracted_numbers = (
        extracted_aadhaar_numbers +
        extracted_pan_numbers +
        extracted_dl_numbers +
        extracted_phone_numbers
    )

    # Underline the numbers in the PDF and save it temporarily
    output_pdf_path = 'data/underlined.pdf'
    underline_numbers_in_pdf(input_pdf_path, output_pdf_path, all_extracted_numbers)

    # Convert underlined PDF to images
    images = convert_pdf_to_images(output_pdf_path)

    # Get the number of pages in the PDF
    no_of_pages = fitz.open(input_pdf_path).page_count

    # Read the underlined PDF file
    with open(output_pdf_path, 'rb') as f:
        underlined_pdf_bytes = f.read()

    # Save the uploaded PDF, underlined PDF, and images to the database
    pdf_id = save_to_db(uploaded_pdf_bytes, underlined_pdf_bytes, images)

    return jsonify({
        "message": "PDF processed and saved successfully",
        "pdf_id": pdf_id,
        "no_of_pages": no_of_pages,
        "extracted_aadhaar_numbers": extracted_aadhaar_numbers,
        "extracted_pan_numbers": extracted_pan_numbers,
        "extracted_dl_numbers": extracted_dl_numbers,
        "extracted_phone_numbers": extracted_phone_numbers
    })

@app.route('/pdf/<int:pdf_id>', methods=['GET'])
def download_pdf(pdf_id):
    pdf_data = get_pdf_from_db(pdf_id)

    key = request.args.get('key')

    if key != api_key:
        return jsonify({"error": "Invalid key"}), 401

    if not pdf_data:
        return jsonify({"error": "PDF not found"}), 404

    return send_file(BytesIO(pdf_data), mimetype='application/pdf', as_attachment=True, download_name='underlined.pdf')

@app.route('/image/<int:pdf_id>/<int:page_number>', methods=['GET'])
def get_image(pdf_id, page_number):
    image_data = get_image_from_db(pdf_id, page_number)

    key = request.args.get('key')

    if key != api_key:
        return jsonify({"error": "Invalid key"}), 401

    if not image_data:
        return jsonify({"error": "Image not found"}), 404

    return send_file(BytesIO(image_data), mimetype='image/png')

@app.route('/pdf_count', methods=['GET'])
def get_pdf_count_route():
    key = request.args.get('key')

    if key != api_key:
        return jsonify({"error": "Invalid key"}), 401

    count = get_pdf_count()
    return jsonify({"count": count})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
