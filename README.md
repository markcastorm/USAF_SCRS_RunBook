# USAF SCRS Investment Report Automation Pipeline (SIMBA)

## Project Overview

This project provides a fully automated pipeline for the South Carolina Retirement System (SCRS) Investment Reports. It dynamically monitors the RSIC website, downloads new quarterly investment reports (PDFs), extracts key financial metrics using semantic PDF parsing, and updates a master CSV file while maintaining its specific formatting and structural integrity.

The pipeline is built on the **SIMBA Architecture**, ensuring modularity, reliability, and dynamic adaptability to website or layout changes.

---

## Architecture Components

### 1. `main.py`

The primary entry point. It triggers the orchestration logic and handles top-level exceptions to ensure clean exits.

### 2. `config.py`

The "brain" of the project. Contains:

* **Paths:** Directory structures for Downloads, Outputs, and Master Data.
* **Mappings:** Semantic mapping between PDF labels (e.g., "Public Equity") and Master CSV internal keys.
* **Settings:** Headless mode toggle and manual date overrides.

### 3. `scraper.py`

A robust, state-aware scraper using **Selenium Stealth** and `requests`:

* **Self-Discovery:** Reads the Master CSV to find the last processed quarter and only downloads newer reports.
* **Human-Like Interaction:** Mimics real user behavior to bypass bot detection.
* **Stable Downloads:** Resolves direct PDF URLs and uses session-aware `requests` for high-reliability downloads.

### 4. `extractor.py`

The "surgical" extraction engine using **PyMuPDF (fitz)**:

* **Semantic Anchoring:** Uses keywords and relative positioning (Total Plan -> $) rather than hardcoded coordinates.
* **Layout Resilience:** Successfully parses standard, accessible, and footnoted PDF formats.
* **Accuracy:** Extracts Market Value and Actual/Target allocations for all asset classes.

### 5. `file_generator.py`

Handles data persistence and formatting:

* **Structure Preservation:** Preserves the unique 2-row header of the master CSV.
* **Formatting Logic:** Restores thousands-separators, quotes, and clean integer strings to match manual data perfectly.
* **Multi-Output:** Generates cleaned Excel files (`.xlsx`) and a ready-to-distribute ZIP package.

### 6. `orchestrator.py`

The pipeline's coordinator. It ensures that if multiple quarters are released, they are processed and appended in the correct chronological order.

---

## Dynamic Features

* **Quarter-Sorting:** Automatically sorts multiple new reports (e.g., Q4 then Q1) before updating the master.
* **Footnote Handling:** Automatically strips footnotes (like "Hedge Funds 6") for matching.
* **Duplicate Prevention:** Never appends a quarter that is already present in the master file.
* **Environment Agnostic:** Fully compatible with Windows (Development) and Linux/Docker (Production).

---

## Setup & Installation

### Prerequisites

* Python 3.10+
* Google Chrome installed
* ChromeDriver (automatically managed if `webdriver-manager` is used, otherwise ensure it's in PATH)

### Installation

1. Install required packages:
   ```bash
   pip install pandas selenium selenium-stealth pymupdf openpyxl requests urllib3
   ```

---

## Usage

### Standard Run

Run the pipeline to check for and process new reports:

```bash
python main.py
```

### Manual Run (Override)

To process a specific date regardless of the master file state, edit `config.py`:

```python
MANUAL_DATE = "2026.03.31" # Set to specific report label
```

---

## Directory Structure

* `Master_Data/`: Contains the ground-truth `Master_USAF_SCRS_DATA.csv`.
* `Output/`:
  * `Latest/`: Always holds the results of the most recent successful run.
  * `YYYYMMDD_HHMMSS/`: Archive of specific runs.
* `Downloads/`: Temporary storage for downloaded PDFs organized by date.
* `Project_information/`: Technical documentation, sample data, and development test scripts.

---

## Security & Integrity

* **No Data Loss:** The script surgically appends new data. It never rewrites or deletes existing rows in the master CSV.
* **SSL Verification:** Configured to handle HTTPS requests safely while allowing flexibility for specific server environments.
