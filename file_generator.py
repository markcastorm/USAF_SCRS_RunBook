import os
import pandas as pd
import shutil
import zipfile
import config
import csv

def update_master_data(new_rows):
    """
    new_rows: list of dicts, each with 'quarter' and data mapping.
    """
    if not new_rows:
        print("No new data to update master.")
        return False

    # Load existing master
    if os.path.exists(config.MASTER_CSV):
        # Read the full file to preserve the top 2 rows exactly
        with open(config.MASTER_CSV, 'r', newline='') as f:
            lines = f.readlines()
        
        # Check if file has data
        if len(lines) < 2:
            print("Master CSV is corrupted or empty.")
            return False

        header1 = lines[0].strip()
        header2 = lines[1].strip()
        
        # Read data rows into DataFrame to check for duplicates
        df = pd.read_csv(config.MASTER_CSV, skiprows=2, header=None)
        df.columns = ["Quarter"] + config.INTERNAL_HEADERS
    else:
        # Create new if doesn't exist
        df = pd.DataFrame(columns=["Quarter"] + config.INTERNAL_HEADERS)
        header1 = "," + ",".join(config.INTERNAL_HEADERS)
        header2 = "," + ",".join([f'"{h}"' for h in config.HUMAN_HEADERS])

    updated = False
    new_lines = []
    for row_data in new_rows:
        q = row_data['quarter']
        if q in df["Quarter"].values:
            print(f"Quarter {q} already exists in master. Skipping.")
            continue
        
        # Build the CSV row manually to match exact formatting
        # Format Market Value with commas and quotes
        market_val = row_data.get("SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS", "NA")
        if market_val != "NA":
            try:
                # Add thousands separator
                formatted_val = f"{int(market_val):,}"
                market_val = f'"{formatted_val}"'
            except:
                pass
        
        row_list = [q, market_val]
        for k in config.INTERNAL_HEADERS[1:]:
            val = row_data.get(k, "NA")
            # Clean up numeric strings
            s_val = str(val).strip()
            if s_val.endswith(".0"):
                s_val = s_val[:-2]
            if s_val.lower() == "n/a":
                s_val = "NA"
            row_list.append(s_val)
        
        new_lines.append(",".join(row_list))
        updated = True
        print(f"Added quarter {q} to master.")

    if updated:
        # Append new lines to the file
        with open(config.MASTER_CSV, 'a', newline='') as f:
            for line in new_lines:
                f.write(line + "\n")
        return True
    return False

def generate_outputs():
    """Generates XLSX, META, and ZIP files."""
    # 1. Generate DATA XLSX
    # Read the updated CSV
    df_full = pd.read_csv(config.MASTER_CSV, header=None)
    data_xls_path = os.path.join(config.RUN_OUTPUT_DIR, "USAF_SCRS_DATA.xlsx")
    df_full.to_excel(data_xls_path, index=False, header=False)

    # 2. Generate META XLSX
    meta_xls_path = os.path.join(config.RUN_OUTPUT_DIR, "USAF_SCRS_META.xlsx")
    if os.path.exists(config.META_FILE):
        shutil.copy(config.META_FILE, meta_xls_path)
    else:
        pd.DataFrame().to_excel(meta_xls_path)

    # 3. Create ZIP
    zip_path = os.path.join(config.RUN_OUTPUT_DIR, "USAF_SCRS_Package.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(data_xls_path, arcname="USAF_SCRS_DATA.xlsx")
        zipf.write(meta_xls_path, arcname="USAF_SCRS_META.xlsx")

    # 4. Update Latest Folder
    if not os.path.exists(config.LATEST_OUTPUT_DIR):
        os.makedirs(config.LATEST_OUTPUT_DIR)
        
    for f in os.listdir(config.LATEST_OUTPUT_DIR):
        os.remove(os.path.join(config.LATEST_OUTPUT_DIR, f))
    
    shutil.copy(data_xls_path, os.path.join(config.LATEST_OUTPUT_DIR, "USAF_SCRS_DATA.xlsx"))
    shutil.copy(meta_xls_path, os.path.join(config.LATEST_OUTPUT_DIR, "USAF_SCRS_META.xlsx"))
    shutil.copy(zip_path, os.path.join(config.LATEST_OUTPUT_DIR, "USAF_SCRS_Package.zip"))
    
    print(f"Outputs generated in {config.RUN_OUTPUT_DIR} and Latest folder.")
