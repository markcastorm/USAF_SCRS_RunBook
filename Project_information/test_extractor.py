import fitz
import os
import config

def extract_pdf_data(pdf_path):
    print(f"Analyzing PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_text_lines = []
    for page in doc:
        text = page.get_text()
        all_text_lines.extend([l.strip() for l in text.split('\n') if l.strip()])

    data = {}
    
    # 1. Extract Total Plan Market Value
    # Look for "Total Plan" followed by "$" in the next few lines
    for i, line in enumerate(all_text_lines):
        if "Total Plan" in line:
            # Check next 3 lines for "$"
            for j in range(i + 1, min(i + 4, len(all_text_lines))):
                if "$" in all_text_lines[j]:
                    val = all_text_lines[j].replace('$', '').replace(',', '').strip()
                    # It might be "( $608)" or similar, we want the first positive large number
                    if '(' not in all_text_lines[j]:
                         data["SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS"] = val
                         print(f"Found Total Plan Market Value: {val}")
                         break
            if "SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS" in data:
                break

    # 2. Extract Allocation Data
    asset_classes = list(config.ASSET_CLASS_MAP.keys())
    for i, line in enumerate(all_text_lines):
        clean_line = line.replace('6', '').strip() # Remove footnote 6
        for ac in asset_classes:
            if clean_line == ac or (ac == "Portable Alpha Hedge Funds" and "Portable Alpha Hedge Funds" in clean_line):
                found_pcts = []
                # Look for percentages in the next 10 lines
                for j in range(i + 1, min(i + 10, len(all_text_lines))):
                    next_val = all_text_lines[j].strip()
                    if "%" in next_val or next_val.lower() == "n/a":
                        found_pcts.append(next_val.replace('%', '').strip())
                    elif len(found_pcts) >= 2: # Stop if we have enough and hit a non-pct
                        break
                
                if len(found_pcts) >= 2:
                    actual = found_pcts[0]
                    target = found_pcts[1]
                    
                    prefix = config.ASSET_CLASS_MAP[ac]
                    actual_key = f"SCRS.{prefix}.ACTUALALLOCATION.NONE.Q.1@SCRS"
                    target_key = f"SCRS.{prefix}.TARGETALLOCATION.NONE.Q.1@SCRS"
                    
                    # For Total Plan, there are two occurrences. 
                    # The one with 100% is the one we want for allocation.
                    if ac == "Total Plan":
                        if actual == "100.0":
                            data[actual_key] = actual
                            data[target_key] = target
                            print(f"Found {ac} Allocation: Actual={actual}, Target={target}")
                    else:
                        if actual_key not in data:
                            data[actual_key] = actual
                            data[target_key] = target
                            print(f"Found {ac}: Actual={actual}, Target={target}")

    doc.close()
    return data

if __name__ == "__main__":
    pdfs = [
        r"D:\Projects\SIMBA-RUNBOOKS\USAF_SCRS_RunBook\Project_information\2025.12.31-investment-report.pdf",
        r"D:\Projects\SIMBA-RUNBOOKS\USAF_SCRS_RunBook\Project_information\2026.03.31-investment-report-accessible.pdf"
    ]
    for test_pdf in pdfs:
        print("="*50)
        results = extract_pdf_data(test_pdf)
        print("\nExtraction Results:")
        for k in config.INTERNAL_HEADERS:
            v = results.get(k, "MISSING")
            print(f"{k}: {v}")
