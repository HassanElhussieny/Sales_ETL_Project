import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR   = BASE_DIR / "data"
LOGS_DIR   = BASE_DIR / "logs"
load_dotenv(dotenv_path=CONFIG_DIR / ".env")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", "5432"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "sales_db"),
}

FILE_PATTERN = "*.xlsx"
TARGET_TABLE = "sales"
LOAD_MODE    = "append"

COLUMN_RENAME_MAP = {
    "Discounts":           "discount",
    "Discount":            "discount",
    "Discount Band":       "discount_band",
    "Units Sold":          "units_sold",
    "Manufacturing Price": "manufacturing_price",
    "Sale Price":          "sale_price",
    "Gross Sales":         "gross_sales",
    " Sales":              "sales",
    "Sales":               "sales",
    "COGS":                "cogs",
    "Profit":              "profit",
    "Month Number":        "month_number",
    "Month Name":          "month_name",
    "Segment":             "segment",
    "Country":             "country",
    "Product":             "product",
    "Date":                "date",
    "Year":                "year",
}

NULL_FILL_RULES = {
    "discount_band": "None",
}

REQUIRED_COLUMNS = ["segment", "country", "product", "date", "sales"]

LOG_FILE   = LOGS_DIR / "pipeline.log"
LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# ── EMAIL SETTINGS ───────────────────────────────────────────
EMAIL_SENDER   = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")


CATEGORY_COLUMNS = ["year", "month_number"]
