import fitz
import os
import config

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
        clean_line = line.replace('6', '').strip()
        for ac in asset_classes:
            if clean_line == ac or (ac == "Portable Alpha Hedge Funds" and "Portable Alpha Hedge Funds" in clean_line):
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
