import re
import fitz

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
        images.append((page_num + 1, img_bytes))
    pdf_document.close()
    return images
