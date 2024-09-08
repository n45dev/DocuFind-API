from flask import request, jsonify, send_file
from io import BytesIO
from src.pdf_processing import extract_numbers_in_pdf, underline_numbers_in_pdf, convert_pdf_to_images
from src.text_processing import extract_numbers_in_text
from src.db import save_pdf_to_db, get_pdf_from_db, get_image_from_db, get_pdf_count
import os
import fitz
from src.config import API_KEY

def register_routes(app):
    @app.route('/upload_pdf', methods=['POST'])
    def upload_pdf():
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        key = request.form.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        uploaded_pdf_bytes = file.read()
        input_pdf_path = 'data/uploaded.pdf'

        with open(input_pdf_path, 'wb') as f:
            f.write(uploaded_pdf_bytes)

        aadhaar_pattern = r"\b\d{4} \d{4} \d{4}\b"
        pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        dl_pattern = r"^(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9]{2})[0-9]{7}$"
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'

        extracted_aadhaar_numbers = extract_numbers_in_pdf(input_pdf_path, aadhaar_pattern)
        extracted_pan_numbers = extract_numbers_in_pdf(input_pdf_path, pan_pattern)
        extracted_dl_numbers = extract_numbers_in_pdf(input_pdf_path, dl_pattern)
        extracted_phone_numbers = extract_numbers_in_pdf(input_pdf_path, phone_pattern)

        all_extracted_numbers = (
            extracted_aadhaar_numbers +
            extracted_pan_numbers +
            extracted_dl_numbers +
            extracted_phone_numbers
        )

        output_pdf_path = 'data/underlined.pdf'
        underline_numbers_in_pdf(input_pdf_path, output_pdf_path, all_extracted_numbers)

        images = convert_pdf_to_images(output_pdf_path)

        no_of_pages = fitz.open(input_pdf_path).page_count

        with open(output_pdf_path, 'rb') as f:
            underlined_pdf_bytes = f.read()

        pdf_id = save_pdf_to_db(uploaded_pdf_bytes, underlined_pdf_bytes, images)

        return jsonify({
            "message": "PDF processed and saved successfully",
            "pdf_id": pdf_id,
            "no_of_pages": no_of_pages,
            "extracted_aadhaar_numbers": extracted_aadhaar_numbers,
            "extracted_pan_numbers": extracted_pan_numbers,
            "extracted_dl_numbers": extracted_dl_numbers,
            "extracted_phone_numbers": extracted_phone_numbers
        })

    @app.route('/upload_text', methods=['POST'])
    def upload_text():
        text = request.form.get('text')
        key = request.form.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        aadhaar_pattern = r"\b\d{4} \d{4} \d{4}\b"
        pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        dl_pattern = r"^(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9]{2})[0-9]{7}$"
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'

        extracted_aadhaar_numbers = extract_numbers_in_text(text, aadhaar_pattern)
        extracted_pan_numbers = extract_numbers_in_text(text, pan_pattern)
        extracted_dl_numbers = extract_numbers_in_text(text, dl_pattern)
        extracted_phone_numbers = extract_numbers_in_text(text, phone_pattern)

        all_extracted_numbers = (
            extracted_aadhaar_numbers +
            extracted_pan_numbers +
            extracted_dl_numbers +
            extracted_phone_numbers
        )

        return jsonify({
            "extracted_aadhaar_numbers": extracted_aadhaar_numbers,
            "extracted_pan_numbers": extracted_pan_numbers,
            "extracted_dl_numbers": extracted_dl_numbers,
            "extracted_phone_numbers": extracted_phone_numbers
        })

    @app.route('/pdf/<int:pdf_id>', methods=['GET'])
    def download_pdf(pdf_id):
        pdf_data = get_pdf_from_db(pdf_id)
        key = request.args.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        if not pdf_data:
            return jsonify({"error": "PDF not found"}), 404

        return send_file(BytesIO(pdf_data), mimetype='application/pdf', as_attachment=True, download_name='underlined.pdf')

    @app.route('/image/<int:pdf_id>/<int:page_number>', methods=['GET'])
    def get_image(pdf_id, page_number):
        image_data = get_image_from_db(pdf_id, page_number)
        key = request.args.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        if not image_data:
            return jsonify({"error": "Image not found"}), 404

        return send_file(BytesIO(image_data), mimetype='image/png')

    @app.route('/pdf_count', methods=['GET'])
    def get_pdf_count_route():
        key = request.args.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        count = get_pdf_count()
        return jsonify({"count": count})
