from PIL import Image
import pytesseract
import re

def extract_numbers_in_image(image_path, pattern):
    numbers = []
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    matches = re.findall(pattern, text)
    numbers.extend(matches)
    return numbers
