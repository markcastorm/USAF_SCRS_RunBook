import scraper
import extractor
import file_generator
import config
import os

def run_pipeline():
    print("Starting USAF SCRS Pipeline...")
    
    # 1. Scrape/Download new reports
    downloaded_files = scraper.scrape_reports()
    
    if not downloaded_files:
        print("No new data to process. Pipeline finished.")
        return

    # 2. Extract data from each new PDF
    all_new_data = []
    for pdf_path in downloaded_files:
        # Extract date from filename or folder
        # The scraper saves in RUN_DOWNLOADS_DIR/date_label/file.pdf
        date_label = os.path.basename(os.path.dirname(pdf_path))
        quarter = scraper.date_to_quarter(date_label)
        
        print(f"Processing {pdf_path} for quarter {quarter}...")
        extracted = extractor.extract_from_pdf(pdf_path)
        if extracted:
            extracted['quarter'] = quarter
            all_new_data.append(extracted)

    # 3. Sort data by quarter to ensure sequential updates
    all_new_data.sort(key=lambda x: scraper.quarter_to_sort_key(x['quarter']))

    # 4. Update master CSV
    if file_generator.update_master_data(all_new_data):
        # 5. Generate output files if master was updated
        file_generator.generate_outputs()
        print("Pipeline execution completed successfully.")
    else:
        print("Master file not updated (likely duplicate data). Output generation skipped.")

if __name__ == "__main__":
    run_pipeline()
