import fitz
import os
import re
import config
from bs4 import BeautifulSoup

def extract_from_pdf(pdf_path):
    """
    Extracts investment data from a single PDF file.
    Returns a dictionary mapping internal keys to values.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return {}

    doc = fitz.open(pdf_path)
    all_text_lines = []
    for page in doc:
        text = page.get_text()
        all_text_lines.extend([l.strip() for l in text.split('\n') if l.strip()])

    data = {}
    
    # 1. Extract Total Plan Market Value
    for i, line in enumerate(all_text_lines):
        if "Total Plan" in line:
            for j in range(i + 1, min(i + 4, len(all_text_lines))):
                if "$" in all_text_lines[j]:
                    val = all_text_lines[j].replace('$', '').replace(',', '').strip()
                    if '(' not in all_text_lines[j]:
                         data["SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS"] = val
                         break
            if "SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS" in data:
                break

    # 2. Extract Allocation Data
    asset_classes = list(config.ASSET_CLASS_MAP.keys())
    for i, line in enumerate(all_text_lines):
        clean_line = re.sub(r'\s*\d+$', '', line).strip()
        for ac in asset_classes:
            if clean_line == ac:
                found_pcts = []
                for j in range(i + 1, min(i + 10, len(all_text_lines))):
                    next_val = all_text_lines[j].strip()
                    if "%" in next_val or next_val.lower() == "n/a":
                        found_pcts.append(next_val.replace('%', '').strip())
                    elif len(found_pcts) >= 2:
                        break
                
                if len(found_pcts) >= 2:
                    actual = found_pcts[0]
                    target = found_pcts[1]
                    
                    prefix = config.ASSET_CLASS_MAP[ac]
                    actual_key = f"SCRS.{prefix}.ACTUALALLOCATION.NONE.Q.1@SCRS"
                    target_key = f"SCRS.{prefix}.TARGETALLOCATION.NONE.Q.1@SCRS"
                    
                    if ac == "Total Plan":
                        if actual == "100.0":
                            data[actual_key] = actual
                            data[target_key] = target
                    else:
                        if actual_key not in data:
                            data[actual_key] = actual
                            data[target_key] = target

    doc.close()
    return data


def extract_from_html(html_path):
    """
    Extracts investment data from an HTML report page (new RSIC format).
    Parses the Exposures table for allocations and market value.
    """
    if not os.path.exists(html_path):
        print(f"Error: HTML not found at {html_path}")
        return {}

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    data = {}
    exposures = soup.find('section', {'id': 'exposures'})
    if not exposures:
        print(f"Error: Could not find exposures section in {html_path}")
        return {}

    table = exposures.find('table')
    if not table:
        return {}

    for row in table.find_all('tr'):
        th = row.find('th', scope='row')
        if not th:
            continue
        cells = row.find_all('td')
        if len(cells) < 3:
            continue

        label = re.sub(r'\s*\d+$', '', th.get_text(strip=True)).strip()
        weight = cells[1].get_text(strip=True).replace('%', '').strip()
        target = cells[2].get_text(strip=True).replace('%', '').strip()

        if target.lower() == 'not applicable':
            target = 'n/a'

        if label == 'Total Plan':
            mv = cells[0].get_text(strip=True).replace(',', '').strip()
            data['SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS'] = mv
            data['SCRS.TOTAL.ACTUALALLOCATION.NONE.Q.1@SCRS'] = weight
            data['SCRS.TOTAL.TARGETALLOCATION.NONE.Q.1@SCRS'] = target
        elif label in config.ASSET_CLASS_MAP:
            prefix = config.ASSET_CLASS_MAP[label]
            data[f'SCRS.{prefix}.ACTUALALLOCATION.NONE.Q.1@SCRS'] = weight
            data[f'SCRS.{prefix}.TARGETALLOCATION.NONE.Q.1@SCRS'] = target

    return data


def extract_from_file(file_path):
    """Dispatches to the correct extractor based on file extension."""
    if file_path.lower().endswith('.html'):
        return extract_from_html(file_path)
    return extract_from_pdf(file_path)
