# USAF_SCRS_RunBook Memory Bank

## Project Overview
Automated pipeline for South Carolina Retirement System (SCRS) investment reports.
- **Source:** [RSIC Investment Reports](https://www.rsic.sc.gov/what-we-do/investment-reports.html)
- **Goal:** Download quarterly PDFs, extract specific investment metrics, update master CSV, and generate output files (XLS, ZIP).
- **Architecture:** SIMBA Pipeline (Config, Scraper, Extractor, File Generator, Orchestrator, Main).

## Data Structure
### Master CSV Headers (Mapping Keys)
- `SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS`: Total Plan Market Value (millions)
- `SCRS.EQUITIES.ACTUALALLOCATION.NONE.Q.1@SCRS`: Public Equity Actual
- `SCRS.BONDS.ACTUALALLOCATION.NONE.Q.1@SCRS`: Bonds Actual
- `SCRS.PRIVATEEQUITY.ACTUALALLOCATION.NONE.Q.1@SCRS`: Private Equity Actual
- `SCRS.PRIVATEDEBT.ACTUALALLOCATION.NONE.Q.1@SCRS`: Private Debt Actual
- `SCRS.REALASSETS.ACTUALALLOCATION.NONE.Q.1@SCRS`: Real Assets Actual
- `SCRS.HEDGEFUNDS.ACTUALALLOCATION.NONE.Q.1@SCRS`: Hedge Funds Actual
- `SCRS.TOTAL.ACTUALALLOCATION.NONE.Q.1@SCRS`: Total Plan Actual (100.0)
- `SCRS.EQUITIES.TARGETALLOCATION.NONE.Q.1@SCRS`: Public Equity Target
- `SCRS.BONDS.TARGETALLOCATION.NONE.Q.1@SCRS`: Bonds Target
- `SCRS.PRIVATEEQUITY.TARGETALLOCATION.NONE.Q.1@SCRS`: Private Equity Target
- `SCRS.PRIVATEDEBT.TARGETALLOCATION.NONE.Q.1@SCRS`: Private Debt Target
- `SCRS.REALASSETS.TARGETALLOCATION.NONE.Q.1@SCRS`: Real Assets Target
- `SCRS.HEDGEFUNDS.TARGETALLOCATION.NONE.Q.1@SCRS`: Hedge Funds Target (n/a)
- `SCRS.TOTAL.TARGETALLOCATION.NONE.Q.1@SCRS`: Total Plan Target (100.0)

## Technical Architecture

### 1. `config.py`
- Stores all constants, file paths, and mappings.
- `COLUMN_MAPPING`: Maps internal keys to human-readable headers.
- `ASSET_CLASS_MAP`: Maps PDF labels to internal key prefixes.
- Handles directory creation for `Output` and `Downloads`.

### 2. `scraper.py`
- **Logic:**
  - Reads `Master_USAF_SCRS_DATA.csv` to find the last processed quarter.
  - Uses Selenium with `selenium_stealth` to navigate the landing page and find report links.
  - **Robust Download:** Instead of browser-triggered downloads, it resolves absolute URLs and uses the `requests` library with session cookies to download PDFs. This bypasses window management issues and is more stable in headless environments.
  - Dynamically detects report dates (YYYY.MM.DD) and converts them to quarters (YYYY-QX).
  - Organizes downloads into `Downloads/TIMESTAMP/DATE_LABEL/` folders.

### 3. `extractor.py`
- **Logic:**
  - Uses `fitz` (PyMuPDF) for text extraction.
  - Sequential line processing for table parsing.
  - **Executive Summary:** Finds "Total Plan" and extracts the subsequent "$" value.
  - **Allocation/Exposure:** Finds asset classes (handling footnotes) and extracts the next 2-10 lines containing percentages.
  - Distinguishes "Total Plan" in the allocation table by verifying the "100.0%" value.

### 4. `file_generator.py`
- **Logic:**
  - Appends new rows to `Master_USAF_SCRS_DATA.csv` if the quarter is not already present.
  - Preserves the original 2-row header structure of the master file.
  - Generates `USAF_SCRS_DATA.xlsx` and `USAF_SCRS_META.xlsx`.
  - Creates a ZIP package for the run.
  - Synchronizes the `Output/Latest/` folder.

### 5. `orchestrator.py`
- Glues the components together.
- Ensures data is sorted chronologically before updating the master.

## Progress Tracker
- [x] Initial Research & Analysis
- [x] Initial `CLAUDE.md` creation
- [x] Create `config.py`
- [x] Implement `scraper.py` (Improved with stable requests-based downloads)
- [x] Implement `extractor.py` (Validated with test script)
- [x] Implement `file_generator.py` (Fixed column mismatch bugs)
- [x] Implement `orchestrator.py`
- [x] Implement `main.py`
- [x] Updated `CLAUDE.md` with full technical context
- [x] Final end-to-end run and validation against sample data

## Key Learning & Fixes
- **Stability:** Using `requests` for downloads after discovery with Selenium is the most robust strategy for SIMBA pipelines.
- **CSV Handling:** Preserving non-standard headers (leading commas, multi-row headers) requires manual line writing combined with Pandas for data rows.
- **Data Integrity:** The orchestrator's duplicate check ensures the pipeline can be run frequently without corrupting the master file.
- **PDF Extraction:** `fitz.get_text()` returns words sequentially; `Total Plan` is often followed by the value on the next line.
- **Footnotes:** Portable Alpha Hedge Funds has a footnote "6" which must be stripped for matching.
- **Headless Compatibility:** Chrome options configured for both Windows and Docker (Linux).
