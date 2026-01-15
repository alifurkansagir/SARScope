"""
Configuration module for SarScope.
Contains constants, user agents, and configuration settings.
"""

import os
from typing import List

# Application Constants
APP_NAME = "SAR-SCOPE"
APP_VERSION = "1.0.0"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "sarscope.db")

# Pricing Configuration
DEFAULT_MIN_MARGIN = 0.05  # 5% minimum margin
UNDERCUTTING_MARGIN = 1.0  # $1 below competitor
MIN_PRICE_THRESHOLD = 1.0  # Minimum allowed price

# Scraping Configuration
REQUEST_TIMEOUT = 10  # seconds
MIN_DELAY = 3  # seconds
MAX_DELAY = 7  # seconds
RETRY_ATTEMPTS = 3

# User Agents Pool
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(os.path.dirname(__file__), "sarscope.log")

# Fuzzy Matching Threshold
FUZZY_MATCH_THRESHOLD = 80  # 80% similarity

# Otomatik Trend Takip Listesi (Sabah 09:30 Raporu İçin)
TREND_WATCHLIST = {
    "Amazon Yapı Market": "https://www.amazon.com.tr/b/?_encoding=UTF8&node=12707123031&bbn=12466724031&ref_=Oct_d_odnav_d_12466724031_0&pd_rd_w=APWkr&content-id=amzn1.sym.0af4f910-f596-42af-95bd-e59dfcd894f8&pf_rd_p=0af4f910-f596-42af-95bd-e59dfcd894f8&pf_rd_r=TFCASYPYM94JWGXM93P5&pd_rd_wg=Quh4m&pd_rd_r=5d1764b8-d4e7-486c-b812-664e81852d19",
    "Trendyol Yapı Market (Markalı/Çok Satan)": "https://www.trendyol.com/sr?wc=103725%2C103720&wb=786%2C102598%2C146324%2C109133%2C110070%2C109187%2C149891&sst=BEST_SELLER",
    "Hepsiburada Yapı Market (Çok Satan)": "https://www.hepsiburada.com/yapi-market-hirdavatlar-c-2147483620?siralama=coksatan"
}

# CLI Configuration
MENU_OPTIONS = {
    "1": "Price Patrol",
    "2": "Trend Hunter",
    "3": "Add Product",
    "4": "View Report",
    "5": "Exit",
}
