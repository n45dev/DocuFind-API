from flask import request, jsonify, send_file
from io import BytesIO
from src.pdf_processing import extract_numbers_in_pdf, underline_numbers_in_pdf, convert_pdf_to_images
from src.image_processing import extract_numbers_in_image
from src.db import save_pdf_to_db, get_pdf_from_db, get_image_from_db, get_pdf_count, create_user_in_db, check_user_exists_in_db, create_company_in_db, get_companies_from_db
import os
import fitz
from src.config import API_KEY
import mysql.connector

def register_routes(app):
    @app.route('/signup', methods=['POST'])
    def create_user():
        key = request.form.get('key')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if key != API_KEY:
            return jsonify({
                "error": "Invalid key"
            }), 401

        if not username or not password or not email or not phone:
            return jsonify({
                "error": "Missing required fields"
            }), 400
        else:
            create_user_in_db(username, password, email, phone)

        return jsonify({
            "message": "User created successfully!",
        })

    @app.route('/signin', methods=['POST'])
    def is_user_exists():
        key = request.form.get('key')
        email = request.form.get('email')
        password = request.form.get('password')

        if key != API_KEY:
            return jsonify({
                "error": "Invalid key"
            }), 401

        if not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            user_exists = check_user_exists_in_db(email, password)

            if user_exists:
                return jsonify({"message": "User exists"}), 200
            else:
                return jsonify({"message": "User does not exist"}), 404

        except Exception as e:
                return jsonify({"error": str(e)}), 500

    @app.route('/create_company', methods=['POST'])
    def create_company():
        key = request.form.get('key')
        company_name = request.form.get('company_name')
        is_mail = request.form.get('is_mail')
        is_phone = request.form.get('is_phone')
        is_aadhaar = request.form.get('is_aadhaar')
        is_pan = request.form.get('is_pan')
        is_dlno = request.form.get('is_dlno')

        if key != API_KEY:
            return jsonify({
                "error": "Invalid key"
            }), 401

        if not company_name or not is_mail or not is_phone or not is_aadhaar or not is_pan or not is_dlno:
            return jsonify({
                "error": "Missing required fields"
            }), 400
        else:
            create_company_in_db(company_name, is_mail, is_phone, is_aadhaar, is_pan, is_dlno)

        return jsonify({
            "message": "Company created successfully!",
        })

    @app.route('/get_companies', methods=['GET'])
    def get_companies():
        key = request.args.get('key')

        if key != API_KEY:
            return jsonify({
                "error": "Invalid key"
            }), 401

        company_details = get_companies_from_db()

        return jsonify({
            "message": "Company details fetched successfully!",
            "company_details": company_details
        })

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
        dl_pattern = r"(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9]{2})[0-9]{7}"
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        email_pattern = r'[\w\.=-]+@[\w\.-]+\.[\w]{2,3}'

        extracted_aadhaar_numbers = extract_numbers_in_pdf(input_pdf_path, aadhaar_pattern)
        extracted_pan_numbers = extract_numbers_in_pdf(input_pdf_path, pan_pattern)
        extracted_dl_numbers = extract_numbers_in_pdf(input_pdf_path, dl_pattern)
        extracted_phone_numbers = extract_numbers_in_pdf(input_pdf_path, phone_pattern)
        extracted_email_addresses = extract_numbers_in_pdf(input_pdf_path, email_pattern)

        all_extracted_numbers = (
            extracted_aadhaar_numbers +
            extracted_pan_numbers +
            extracted_dl_numbers +
            extracted_phone_numbers +
            extracted_email_addresses
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
            "extracted_phone_numbers": extracted_phone_numbers,
            "extracted_email_addresses": extracted_email_addresses
        })

    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        key = request.form.get('key')

        if key != API_KEY:
            return jsonify({"error": "Invalid key"}), 401

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        aadhaar_pattern = r"\b\d{4} \d{4} \d{4}\b"
        pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        dl_pattern = r"(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9]{2})[0-9]{7}"
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        email_pattern = r'[\w\.=-]+@[\w\.-]+\.[\w]{2,3}'

        extracted_aadhaar_numbers = extract_numbers_in_image(file, aadhaar_pattern)
        extracted_pan_numbers = extract_numbers_in_image(file, pan_pattern)
        extracted_dl_numbers = extract_numbers_in_image(file, dl_pattern)
        extracted_phone_numbers = extract_numbers_in_image(file, phone_pattern)
        extracted_email_addresses = extract_numbers_in_pdf(file, email_pattern)

        all_extracted_numbers = (
            extracted_aadhaar_numbers +
            extracted_pan_numbers +
            extracted_dl_numbers +
            extracted_phone_numbers +
            extracted_email_addresses
        )

        return jsonify({
            "extracted_aadhaar_numbers": extracted_aadhaar_numbers,
            "extracted_pan_numbers": extracted_pan_numbers,
            "extracted_dl_numbers": extracted_dl_numbers,
            "extracted_phone_numbers": extracted_phone_numbers,
            "extracted_email_addresses": extracted_email_addresses
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
