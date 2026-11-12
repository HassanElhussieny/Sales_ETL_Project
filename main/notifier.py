# =============================================================
# main/notifier.py
# =============================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import traceback
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, LOG_FILE
from main.logger import get_logger

logger = get_logger("notifier")


def _send_email(subject: str, body: str) -> bool:

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        logger.warning("Email credentials missing — skipping notification")
        return False

    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        logger.info(f"  → Email sent to {EMAIL_RECEIVER} ✓")
        return True

    except Exception as e:
        logger.error(f"  → Failed to send email: {e}")
        return False


def notify_success(rows_extracted: int, rows_loaded: int,
                   rows_dropped: int, total_time: float):

    subject = "✅ ETL Pipeline — Completed Successfully"

    body = f"""
Hello!

Your ETL Sales Pipeline completed successfully.

📊 SUMMARY
──────────────────────────────
Rows extracted  : {rows_extracted}
Rows loaded     : {rows_loaded}
Rows dropped    : {rows_dropped}
Total time      : {total_time}s
──────────────────────────────

Data is now available in PostgreSQL → table: sales

This is an automated message from your ETL pipeline.
    """.strip()

    logger.info("Sending success notification email...")
    _send_email(subject, body)


def notify_failure(error_message: str):

    subject = "❌ ETL Pipeline — FAILED"

    body = f"""
Hello!

Your ETL Sales Pipeline FAILED and needs attention!

🔴 ERROR DETAILS
──────────────────────────────
{error_message}
──────────────────────────────

Check the full logs at:
{LOG_FILE}

This is an automated message from your ETL pipeline.
    """.strip()

    logger.info("Sending failure notification email...")
    _send_email(subject, body)
