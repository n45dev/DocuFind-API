import os
from flask.wrappers import json
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),
        port=os.environ.get('MYSQL_PORT'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE')
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create pdf_files table
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        uploaded_pdf LONGBLOB,
                        underlined_pdf LONGBLOB)''')
    # Create pdf_images table
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_images (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        page_number INT,
                        image LONGBLOB,
                        pdf_id INT,
                        FOREIGN KEY (pdf_id) REFERENCES pdf_files (id))''')
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255),
                        password VARCHAR(255),
                        email VARCHAR(255),
                        phone_number VARCHAR(255),
                        aadhaar_number VARCHAR(255),
                        pan_number VARCHAR(255),
                        dl_number VARCHAR(255));''')
    # Create companies table
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        company_name VARCHAR(255),
                        is_mail BOOL,
                        is_phone BOOL,
                        is_aadhaar BOOL,
                        is_pan BOOL,
                        is_dlno BOOL
                    );''')
    conn.commit()
    cursor.close()
    conn.close()

def save_pdf_to_db(uploaded_pdf_bytes, underlined_pdf_bytes, images):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pdf_files (uploaded_pdf, underlined_pdf) VALUES (%s, %s)",
                   (uploaded_pdf_bytes, underlined_pdf_bytes))
    pdf_id = cursor.lastrowid

    for page_number, image in images:
        cursor.execute("INSERT INTO pdf_images (page_number, image, pdf_id) VALUES (%s, %s, %s)",
                       (page_number, image, pdf_id))

    conn.commit()
    cursor.close()
    conn.close()
    return pdf_id

def get_pdf_from_db(pdf_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT underlined_pdf FROM pdf_files WHERE id = %s", (pdf_id,))
    pdf_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return pdf_data[0] if pdf_data else None

def get_image_from_db(pdf_id, page_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM pdf_images WHERE pdf_id = %s AND page_number = %s", (pdf_id, page_number))
    image_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return image_data[0] if image_data else None

def get_pdf_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pdf_files")
    count = cursor.fetchone()
    cursor.close()
    conn.close()
    return count[0] if count else None

def create_user_in_db(username, password, email, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)", (username, password, email, phone))
    conn.commit()
    cursor.close()
    conn.close()

def check_user_exists_in_db(email, password):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))

        results = cursor.fetchall()
        return len(results) > 0

    except mysql.connector.Error as err:
        raise Exception(f"Database error: {str(err)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_company_in_db(company_name, is_mail, is_phone, is_aadhaar, is_pan, is_dlno):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO companies (company_name, is_mail, is_phone, is_aadhaar, is_pan, is_dlno) VALUES (%s, %s, %s, %s, %s, %s)", (company_name, is_mail, is_phone, is_aadhaar, is_pan, is_dlno))
    conn.commit()
    cursor.close()
    conn.close()

def get_companies_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM companies")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def update_user_data_in_db(email, aadhaar_number, pan_number, dl_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET aadhaar_number = %s,
            pan_number = %s,
            dl_number = %s
        WHERE email = %s;
        ''', (aadhaar_number, pan_number, dl_number, email))
    conn.commit()
    cursor.close()
    conn.close()

def get_users_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_user_from_db(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
