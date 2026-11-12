import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import COLUMN_RENAME_MAP, NULL_FILL_RULES, REQUIRED_COLUMNS
from main.logger import get_logger

logger = get_logger("transform")

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Standardizing column names...")

    # strip spaces
    df.columns = df.columns.str.strip()

    #  rename using our map
    df = df.rename(columns=COLUMN_RENAME_MAP, errors="ignore")

    #  auto clean remaining columns
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    # remove duplicate columns, keep first occurrence
    df = df.loc[:, ~df.columns.duplicated()]

    logger.info(f"  → Final columns: {list(df.columns)}")
    return df


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Fixing data types...")
    numeric_cols = [
        "units_sold", "manufacturing_price", "sale_price",
        "gross_sales", "discount", "sales", "cogs", "profit",
        "month_number", "year"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        logger.info(f"  → Date range: {df['date'].min()} to {df['date'].max()}")

    string_cols = ["segment", "country", "product", "discount_band",
                   "month_name", "source_file"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Handling null values...")
    before = len(df)
    for col, fill_value in NULL_FILL_RULES.items():
        if col in df.columns:
            nulls_count = df[col].isna().sum()
            if nulls_count > 0:
                df[col] = df[col].fillna(fill_value)
                logger.info(f"  → Filled {nulls_count} nulls in '{col}' with '{fill_value}'")
    df = df.dropna(subset=[c for c in REQUIRED_COLUMNS if c in df.columns])
    dropped = before - len(df)
    if dropped > 0:
        logger.warning(f"  → Dropped {dropped} rows with nulls in required columns")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Checking for duplicate rows...")
    before = len(df)
    check_cols = [c for c in df.columns if c != "source_file"]
    df = df.drop_duplicates(subset=check_cols)
    dropped = before - len(df)
    logger.info(f"  → Removed {dropped} duplicate rows")
    return df


def add_audit_columns(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Adding audit columns...")
    df["loaded_at"] = pd.Timestamp.now()
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        logger.warning("Empty DataFrame received — skipping transform.")
        return df

    logger.info(f"Starting transform on {len(df)} rows...")
    df = standardize_column_names(df)
    df = fix_data_types(df)
    df = handle_nulls(df)
    df = remove_duplicates(df)
    df = add_audit_columns(df)
    logger.info(f"Transform complete — {len(df)} clean rows ready to load")
    return df