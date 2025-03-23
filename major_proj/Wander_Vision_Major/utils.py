# utils.py
import re

def clean_direction_text(direction):
    clean_text = re.sub(r"<.*?>", "", direction)
    clean_text = re.sub(r"Pass by.*?(?=\(|$)", "", clean_text).strip()
    return clean_text


