import pandas as pd
from pathlib import Path
from typing import List
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import DATA_DIR, FILE_PATTERN
from main.logger import get_logger

logger = get_logger("extract")


def discover_files() -> List[Path]:
    logger.info(f"Scanning for files in: {DATA_DIR}")
    
    files = sorted(DATA_DIR.glob(FILE_PATTERN))
    
    if not files:
        logger.warning(f"No files found matching '{FILE_PATTERN}' in {DATA_DIR}")
        return []
    
    logger.info(f"Found {len(files)} file(s): {[f.name for f in files]}")
    return files


def read_excel_file(filepath: Path) -> pd.DataFrame:
    logger.info(f"Reading file: {filepath.name}")
    
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        logger.info(f"  → Loaded {len(df)} rows x {len(df.columns)} columns")
        df["source_file"] = filepath.name
        return df
    
    except Exception as e:
        logger.error(f"  → FAILED to read {filepath.name}: {e}")
        return None


def extract_all() -> pd.DataFrame:
    files = discover_files()
    
    if not files:
        return pd.DataFrame()
    
    dataframes = []
    
    for filepath in files:
        df = read_excel_file(filepath)
        if df is not None:
            dataframes.append(df)
    
    if not dataframes:
        logger.error("No files could be read. Pipeline stopping.")
        return pd.DataFrame()
    
    combined = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Extract complete — total rows combined: {len(combined)}")
    return combined
