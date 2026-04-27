import re

def clean_text(text):
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters but keep punctuation
    # (Basic preprocessing)
    return text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned = clean_text(content)
        print(cleaned)
