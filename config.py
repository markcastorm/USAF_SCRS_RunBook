import os
from datetime import datetime

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "Project_information")
MASTER_DATA_DIR = os.path.join(BASE_DIR, "Master_Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "Downloads")

# File Paths
MASTER_CSV = os.path.join(MASTER_DATA_DIR, "Master_USAF_SCRS_DATA.csv")
META_FILE = os.path.join(PROJECT_DIR, "USAF_SCRS_META_20250616.xlsx")

# Scraper Settings
BASE_URL = "https://www.rsic.sc.gov/what-we-do/investment-reports.html"
HEADLESS = True  # Set to False for debugging
MANUAL_DATE = None  # Set to a date string like '2026.03.31' to override dynamic detection

# Extraction Settings (Keywords for table identification)
EXECUTIVE_SUMMARY_KEYWORDS = ["Executive Summary", "Market Value", "(millions)", "Total Plan"]
ALLOCATION_KEYWORDS = ["Allocation / Exposure", "Portfolio", "Policy Target", "Public Equity"]

# Column Mappings (Internal Keys -> Human Readable)
COLUMN_MAPPING = {
    "SCRS.TOTAL.LEVEL.NONE.Q.1@SCRS": "Total Plan",
    "SCRS.EQUITIES.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Public Equity",
    "SCRS.BONDS.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Bonds",
    "SCRS.PRIVATEEQUITY.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Private Equity",
    "SCRS.PRIVATEDEBT.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Private Debt",
    "SCRS.REALASSETS.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Real Assets",
    "SCRS.HEDGEFUNDS.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Portable Alpha Hedge Funds",
    "SCRS.TOTAL.ACTUALALLOCATION.NONE.Q.1@SCRS": "Actual Allocation, Total Plan",
    "SCRS.EQUITIES.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Public Equity",
    "SCRS.BONDS.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Bonds",
    "SCRS.PRIVATEEQUITY.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Private Equity",
    "SCRS.PRIVATEDEBT.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Private Debt",
    "SCRS.REALASSETS.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Real Assets",
    "SCRS.HEDGEFUNDS.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Portable Alpha Hedge Funds",
    "SCRS.TOTAL.TARGETALLOCATION.NONE.Q.1@SCRS": "Target Allocation, Total Plan"
}

# Ordered Headers for CSV (Exactly as they appear in master)
INTERNAL_HEADERS = list(COLUMN_MAPPING.keys())
HUMAN_HEADERS = list(COLUMN_MAPPING.values())

# Asset Class Mapping (PDF Label -> Internal Key Prefix)
# Note: "Public Equity" in PDF maps to "EQUITIES" in keys
ASSET_CLASS_MAP = {
    "Public Equity": "EQUITIES",
    "Bonds": "BONDS",
    "Private Equity": "PRIVATEEQUITY",
    "Private Debt": "PRIVATEDEBT",
    "Real Assets": "REALASSETS",
    "Portable Alpha Hedge Funds": "HEDGEFUNDS",
    "Total Plan": "TOTAL"
}

# Directories for current run
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_OUTPUT_DIR = os.path.join(OUTPUT_DIR, TIMESTAMP)
LATEST_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "Latest")
RUN_DOWNLOADS_DIR = os.path.join(DOWNLOADS_DIR, TIMESTAMP)

# Create necessary directories
for d in [OUTPUT_DIR, DOWNLOADS_DIR, RUN_OUTPUT_DIR, LATEST_OUTPUT_DIR, RUN_DOWNLOADS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)
