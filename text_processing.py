import re

def extract_numbers_in_text(text, pattern):
    return re.findall(pattern, text)
