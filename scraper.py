import os
import time
import random
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from urllib.parse import urljoin
import config

def get_last_quarter_from_master():
    """Reads the master CSV and returns the latest quarter string (e.g., '2025-Q3')."""
    if not os.path.exists(config.MASTER_CSV):
        return None
    try:
        # Read raw to get the very last row
        df = pd.read_csv(config.MASTER_CSV, skiprows=2, header=None)
        if df.empty:
            return None
        last_q = df.iloc[-1, 0]
        return last_q
    except Exception as e:
        print(f"Error reading master CSV: {e}")
        return None

def date_to_quarter(date_str):
    """Converts a date string like '2025.12.31' to a quarter like '2025-Q4'."""
    try:
        parts = date_str.split('.')
        year = parts[0]
        month = parts[1]
        if month == '03': return f"{year}-Q1"
        if month == '06': return f"{year}-Q2"
        if month == '09': return f"{year}-Q3"
        if month == '12': return f"{year}-Q4"
    except:
        pass
    return None

def quarter_to_sort_key(q_str):
    """Converts '2025-Q3' to a comparable integer (20253)."""
    if not q_str: return 0
    try:
        return int(q_str.replace('-Q', ''))
    except:
        return 0

def setup_driver():
    chrome_options = Options()
    if config.HEADLESS:
        chrome_options.add_argument("--headless=new") # Modern headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver

def download_file(url, dest_path, session_cookies=None):
    """Downloads a file using requests."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    cookies = {c['name']: c['value'] for c in session_cookies} if session_cookies else {}
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return False

def scrape_reports():
    last_q = get_last_quarter_from_master()
    print(f"Last quarter in master: {last_q}")
    last_q_key = quarter_to_sort_key(last_q)

    driver = setup_driver()
    downloaded_files = []

    try:
        print(f"Navigating to {config.BASE_URL}...")
        driver.get(config.BASE_URL)
        time.sleep(random.uniform(3, 5))

        # Get all cookies for requests
        session_cookies = driver.get_cookies()

        # Find all report links
        report_links = driver.find_elements(By.CSS_SELECTOR, ".reportRow .reportListItem a")
        
        to_download = []
        for link in report_links:
            text = link.text.strip()
            href = link.get_attribute("href")
            
            # Use urljoin to ensure absolute URL
            abs_url = urljoin(driver.current_url, href)
            
            q = date_to_quarter(text)
            if q:
                if config.MANUAL_DATE:
                    if text == config.MANUAL_DATE:
                        to_download.append((text, abs_url))
                else:
                    q_key = quarter_to_sort_key(q)
                    if q_key > last_q_key:
                        to_download.append((text, abs_url))

        if not to_download:
            print("No new reports found.")
            return []

        print(f"Found {len(to_download)} new reports to download.")

        # Download reports using requests
        for date_label, pdf_url in to_download:
            print(f"Downloading report for {date_label}: {pdf_url}")
            
            # Create subfolder for this specific date
            date_dir = os.path.join(config.RUN_DOWNLOADS_DIR, date_label)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
            
            filename = f"investment-report-{date_label}.pdf"
            dest_path = os.path.join(date_dir, filename)
            
            if download_file(pdf_url, dest_path, session_cookies):
                print(f"Successfully downloaded: {dest_path}")
                downloaded_files.append(dest_path)
            else:
                # Retry without cookies just in case
                if download_file(pdf_url, dest_path):
                    print(f"Successfully downloaded (no cookies): {dest_path}")
                    downloaded_files.append(dest_path)

    finally:
        driver.quit()

    return downloaded_files

if __name__ == "__main__":
    # Test run
    downloaded = scrape_reports()
    print(f"Downloaded: {downloaded}")

if __name__ == "__main__":
    downloaded = scrape_reports()
    print(f"Downloaded: {downloaded}")
