import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import DB_CONFIG, TARGET_TABLE, LOAD_MODE
from main.logger import get_logger

logger = get_logger("load")


def build_connection_string() -> str:
    return (
        f"postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        f"/{DB_CONFIG['database']}"
    )


def get_engine():
    conn_str = build_connection_string()
    logger.info(
        f"Connecting to PostgreSQL at "
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("  → Database connection successful ✓")
        return engine
    except Exception as e:
        logger.error(f"  → Failed to connect to database: {e}")
        raise


def load(df: pd.DataFrame) -> bool:
    if df.empty:
        logger.warning("Empty DataFrame — nothing to load.")
        return False

    engine = get_engine()
    logger.info(
        f"Loading {len(df)} rows into "
        f"table '{TARGET_TABLE}' (mode: {LOAD_MODE})..."
    )

    try:
        df.to_sql(
            name      = TARGET_TABLE,
            con       = engine,
            if_exists = LOAD_MODE,
            index     = False,
            chunksize = 500,
            method    = "multi"
        )

        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {TARGET_TABLE}"))
            total_rows = result.scalar()

        logger.info(
            f"  → Load successful ✓ | "
            f"Table '{TARGET_TABLE}' now has {total_rows} total rows"
        )
        return True

    except Exception as e:
        logger.error(f"  → Load FAILED: {e}")
        return False

    finally:
        engine.dispose()
        logger.info("  → Database connection closed")