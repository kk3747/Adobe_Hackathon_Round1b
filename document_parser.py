import pdfplumber
import re
import wordninja

def add_spaces(text):
    # First, apply the regex splitting as before
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    s = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', s)
    s = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', s)

    # If still few or no spaces, use wordninja to split it!
    # Only apply if there are long runs without space (e.g., > 20 chars).
    tokens = []
    for part in s.split():
        if len(part) > 15 and part.count(' ') == 0:
            tokens.extend(wordninja.split(part))
        else:
            tokens.append(part)
    s = ' '.join(tokens)
    # Remove double spaces that may result
    return re.sub(r'\s+', ' ', s).strip()

def is_valid_section_title(title):
    blacklist = [
        "references", "acknowledgements", "author details", "received", "published", 
        "data access statement", "nonewdatawerecreated", "abstract", "keywords", "introduction"
    ]
    title_lower = title.lower()
    if any(bl in title_lower for bl in blacklist):
        return False

    words = title.split()
    if len(words) > 10:
        return False
    if title.endswith('.'):
        return False

    alpha_chars = sum(c.isalpha() for c in title)
    if alpha_chars < max(3, len(title)*0.4):
        return False

    return True

def extract_sections(filepath):
    sections = []
    with pdfplumber.open(filepath) as pdf:
        current_section = None
        current_text = []
        current_page = None

        heading_pattern = re.compile(r'^\d*\.?\d*\s*[A-Z][A-Za-z0-9 ,\-:()]+(:)?$')

        for page_no, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            lines = text.split('\n')
            for line in lines:
                line_stripped = line.strip()
                if heading_pattern.match(line_stripped):
                    # Save previous section if exists
                    if current_section is not None:
                        sections.append({
                            "document": filepath,
                            "page": current_page,
                            "section_title": add_spaces(current_section.rstrip(':').strip()),
                            "section_text": "\n".join(current_text).strip()
                        })
                    current_section = line_stripped
                    current_text = []
                    current_page = page_no
                else:
                    if current_section is not None:
                        current_text.append(line)

        if current_section is not None:
            sections.append({
                "document": filepath,
                "page": current_page,
                "section_title": add_spaces(current_section.rstrip(':').strip()),
                "section_text": "\n".join(current_text).strip()
            })

    # Merge or remove invalid titles by merging their text into previous valid section
    filtered_sections = []
    for sec in sections:
        if is_valid_section_title(sec["section_title"]):
            filtered_sections.append(sec)
        else:
            if filtered_sections:
                filtered_sections[-1]["section_text"] += "\n" + sec["section_text"]
            else:
                filtered_sections.append(sec)

    return filtered_sections
