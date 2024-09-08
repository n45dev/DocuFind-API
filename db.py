import os
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
