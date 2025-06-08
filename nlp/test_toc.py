import fitz  # PyMuPDF
import yaml
import re
from collections import OrderedDict


def extract_builtin_toc(doc):
    toc = doc.get_toc(simple=True)
    return toc if toc else None


import fitz
import re

def extract_verified_toc(doc, max_pages_to_scan=10, max_toc_items=30, content_page_num=None):
    toc = []
    seen = set()

    # Get text from first few pages
    if content_page_num is not None:
        # If a specific content page is provided, use it
        try:
            page_text = doc.load_page(content_page_num - 1).get_text()
            full_text = page_text + '\n'
        except Exception:
            print(f"⚠️ Could not load content page {content_page_num}. Scanning first {max_pages_to_scan} pages instead.")
            full_text = ''
    else:
        for i in range(min(max_pages_to_scan, doc.page_count)):
            full_text += doc.load_page(i).get_text() + '\n'

    # Split around number boundaries (assumes numbers might be page numbers)
    parts = re.split(r'(\d{1,4})', full_text)

    # Scan for pattern: [section_title, page_number]
    for i in range(len(parts) - 1):
        part = parts[i].strip()
        next_part = parts[i + 1].strip()

        # Current part = title candidate, next part = page number?
        if part and next_part.isdigit():
            page_num = int(next_part)
            if 1 <= page_num <= doc.page_count:
                # Validate: does this section title appear in the suggested page?
                try:
                    page_text = doc.load_page(page_num - 1).get_text()
                except Exception:
                    continue
                normalized_title = re.sub(r'\s+', ' ', part).strip()
                if normalized_title.lower() in page_text.lower():
                    key = (normalized_title.lower(), page_num)
                    if key not in seen:
                        toc.append([1, normalized_title, page_num])
                        seen.add(key)

        # Limit to reasonable TOC size
        if len(toc) >= max_toc_items:
            break

    return toc if toc else None


def detect_toc_via_regex(doc, max_pages=10):
    toc = []

    # Pattern 1: title followed by dots and page number
    title_first = re.compile(r'(.*?[A-Za-z].*?)\s*\.{2,}\s*(\d+)', re.DOTALL)

    # Pattern 2: page number followed by space/tab/newline and title
    page_first = re.compile(r'(\d+)[\t\r\n ]+(.*?[A-Za-z].*?)(?=(\d+)[\t\r\n ]|$)', re.DOTALL)

    for i in range(min(max_pages, doc.page_count)):
        text = doc.load_page(i).get_text()

        # The word Content must be on the page, else skip
        if "content" not in str.lower(text):
            continue

        print(text)
        
        # Break page text on 'number' boundaries
        parts = re.findall(r'\D+|\d+', text)

        # 

        # Match title-first pattern (e.g., "Executive Summary .......... 12")
        for match in title_first.finditer(text):
            title = match.group(1).strip().replace('\n', ' ')
            page = int(match.group(2))
            toc.append([1, title, page])

        # Match page-first pattern (e.g., "12    Executive Summary")
        for match in page_first.finditer(text):
            page = int(match.group(1))
            title = match.group(2).strip().replace('\n', ' ')
            toc.append([1, title, page])

        if len(toc) >= 3:
            return toc

    return None

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def extract_text_by_page_range(doc, start, end):
    text = ""
    for page_num in range(start, end):
        page = doc.load_page(page_num)
        text += page.get_text() + "\n"
    return clean_text(text)


def build_section_ranges(toc, total_pages):
    section_ranges = []
    for idx, entry in enumerate(toc):
        level, title, page = entry
        start = page - 1  # PyMuPDF uses 0-based page numbers
        end = toc[idx + 1][2] - 1 if idx + 1 < len(toc) else total_pages
        section_ranges.append((title.strip(), start, end))
    return section_ranges


def extract_sections_to_yaml(pdf_path, yaml_path):
    doc = fitz.open(pdf_path)

    # Built-in isn't reliable
    # toc = extract_builtin_toc(doc)
    # if not toc:
        # print("⚠️ Built-in TOC not found. Attempting regex-based detection...")
    # toc = detect_toc_via_regex(doc)
    toc = extract_verified_toc(doc, content_page_num=3)
    if not toc:
        print("❌ TOC could not be identified.")
        return
    else:
        print(toc)

    exit()

    total_pages = doc.page_count
    section_ranges = build_section_ranges(toc, total_pages)

    output = OrderedDict()

    for title, start, end in section_ranges:
        print(f"📖 Extracting: {title} (Pages {start + 1} to {end})")
        section_text = extract_text_by_page_range(doc, start, end)
        if section_text:
            output[title] = section_text

    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, sort_keys=False)

    print(f"\n✅ YAML output written to: {yaml_path}")


# Example usage

fname = r"C:\Users\sunny\sunny_tools_data\finance\chatpdf\2025-04_ECT_Shilchar.pdf"
fname = r"H:\My Drive\Financials\Stock Analysis\Nvidia\AR_Nvidia_2024.pdf"
fname = r"H:\My Drive\Financials\Stock Analysis\HUL\HUL-AR-2024-25.pdf"
fname = r"H:\My Drive\Financials\Stock Analysis\Inox India\AR_InoxIndia_FY2024-25.pdf"

fyml = fname + ".yml"  # output filename

extract_sections_to_yaml(fname, fyml)
