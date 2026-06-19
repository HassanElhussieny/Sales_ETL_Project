import time
import traceback
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main.extract   import extract_all
from main.transform import transform
from main.load      import load
from main.logger    import get_logger
from main.notifier  import notify_success, notify_failure

logger = get_logger("pipeline")

def run_pipeline():
    pipeline_start = time.time()

    logger.info("=" * 60)
    logger.info("  ETL PIPELINE STARTED")
    logger.info("=" * 60)

    try:
        # ── PHASE 1: EXTRACT ──────────────────────────
        logger.info("[ PHASE 1 ] EXTRACT")
        t0 = time.time()
        raw_df = extract_all()
        extract_time = round(time.time() - t0, 2)
        logger.info(f"  Extract finished in {extract_time}s — {len(raw_df)} raw rows")

        if raw_df.empty:
            raise ValueError("No data extracted — check data/ folder")

        # ── PHASE 2: TRANSFORM ────────────────────────
        logger.info("[ PHASE 2 ] TRANSFORM")
        t0 = time.time()
        clean_df = transform(raw_df)
        transform_time = round(time.time() - t0, 2)
        logger.info(f"  Transform finished in {transform_time}s — {len(clean_df)} clean rows")

        if clean_df.empty:
            raise ValueError("No rows survived transformation")

        # ── PHASE 3: LOAD ─────────────────────────────
        logger.info("[ PHASE 3 ] LOAD")
        t0 = time.time()
        success = load(clean_df)
        load_time = round(time.time() - t0, 2)

        if not success:
            raise ValueError("Load to PostgreSQL failed")

        # ── SUCCESS ───────────────────────────────────
        total_time = round(time.time() - pipeline_start, 2)

        logger.info("=" * 60)
        logger.info("  ETL PIPELINE COMPLETED SUCCESSFULLY ✓")
        logger.info(f"  Rows extracted  : {len(raw_df)}")
        logger.info(f"  Rows loaded     : {len(clean_df)}")
        logger.info(f"  Rows dropped    : {len(raw_df) - len(clean_df)}")
        logger.info(f"  Total time      : {total_time}s")
        logger.info("=" * 60)

        notify_success(
            rows_extracted = len(raw_df),
            rows_loaded    = len(clean_df),
            rows_dropped   = len(raw_df) - len(clean_df),
            total_time     = total_time
        )
        return True

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error("=" * 60)
        logger.error("  ETL PIPELINE FAILED")
        logger.error(f"  {e}")
        logger.error("=" * 60)
        notify_failure(error_details)
        return False


if __name__ == "__main__":
    run_pipeline()
