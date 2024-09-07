import re
import fitz
from flask import Flask, request, jsonify, send_file
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                # Top side
                page.draw_line((inst.x0, inst.y0), (inst.x1, inst.y0), color=(0, 1, 0), width=1)
                # Bottom side
                page.draw_line((inst.x0, inst.y1), (inst.x1, inst.y1), color=(0, 1, 0), width=1)
                # Left side
                page.draw_line((inst.x0, inst.y0), (inst.x0, inst.y1), color=(0, 1, 0), width=1)
                # Right side
                page.draw_line((inst.x1, inst.y0), (inst.x1, inst.y1), color=(0, 1, 0), width=1)
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

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    key = request.form.get('key')

    if key != 'stop_hacking_srinath':
        return jsonify({"error": "Invalid key"}), 401

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read the uploaded PDF file
    uploaded_pdf_bytes = file.read()
    input_pdf_path = 'uploaded.pdf'

    # Save the uploaded file temporarily to extract text
    with open(input_pdf_path, 'wb') as f:
        f.write(uploaded_pdf_bytes)

    # Define patterns for Aadhaar, PAN, DL, and phone numbers
    aadhaar_pattern = ("^[2-9]{1}[0-9]{3}\\" + "s[0-9]{4}\\s[0-9]{4}$")
    pan_pattern = "[A-Z]{5}[0-9]{4}[A-Z]{1}"
    dl_pattern = ("^(([A-Z]{2}[0-9]{2})" + "( )|([A-Z]{2}-[0-9]" + "{2}))((19|20)[0-9]" + "[0-9])[0-9]{7}$")
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
    output_pdf_path = 'underlined.pdf'
    underline_numbers_in_pdf(input_pdf_path, output_pdf_path, all_extracted_numbers)

    # Convert underlined PDF to images
    images = convert_pdf_to_images(output_pdf_path)

    # Get the number of pages in the PDF
    no_of_pages = fitz.open(input_pdf_path).page_count

    # Read the underlined PDF file
    with open(output_pdf_path, 'rb') as f:
        underlined_pdf_bytes = f.read()

    return jsonify({
        "aadhaar_numbers": extracted_aadhaar_numbers,
        "pan_numbers": extracted_pan_numbers,
        "dl_numbers": extracted_dl_numbers,
        "phone_numbers": extracted_phone_numbers
    })

@app.route('/pdf', methods=['POST'])
def download_pdf():
    uploaded_file = request.files['file']
    uploaded_pdf_bytes = uploaded_file.read()

    key = request.form.get('key')

    if key != 'stop_hacking_srinath':
        return jsonify({"error": "Invalid key"}), 401

    return send_file(BytesIO(uploaded_pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name='underlined.pdf')

@app.route('/image/<int:page_number>', methods=['POST'])
def get_image(page_number):
    uploaded_file = request.files['file']
    uploaded_pdf_bytes = uploaded_file.read()

    key = request.form.get('key')

    if key != 'stop_hacking_srinath':
        return jsonify({"error": "Invalid key"}), 401

    input_pdf_path = 'uploaded.pdf'

    with open(input_pdf_path, 'wb') as f:
        f.write(uploaded_pdf_bytes)

    images = convert_pdf_to_images(input_pdf_path)

    if page_number > len(images) or page_number < 1:
        return jsonify({"error": "Page number out of range"}), 404

    page_number, image_data = images[page_number - 1]

    return send_file(BytesIO(image_data), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
