"""
Google Sheets service — fetches Google Form responses from a linked Google Sheet.

Prerequisites:
    1. Enable the Google Sheets API in your Google Cloud project.
    2. Create a Service Account and download the JSON credentials file.
    3. Share the target Google Sheet with the service account's email.
    4. Set GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEET_ID, and
       GOOGLE_SHEET_NAME in your .env file.
"""

from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Required scopes for read-only access to Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_gspread_client() -> gspread.Client:
    """Authenticate and return a gspread client using service-account credentials."""
    creds = Credentials.from_service_account_file(
        settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def fetch_form_responses() -> list[dict[str, Any]]:
    """
    Fetch all rows from the configured Google Sheet and return them as a list
    of dictionaries keyed by the header row.

    Expected sheet columns (matching the Google Form fields):
        Timestamp | IP Address | Domain | Malware Hash | Threat Type | Description

    Returns:
        A list of dicts, e.g.:
        [
            {
                "Timestamp": "2026-03-01 10:00:00",
                "IP Address": "10.0.0.5",
                "Domain": "",
                "Malware Hash": "",
                "Threat Type": "malware",
                "Description": "Suspicious outbound traffic"
            },
            ...
        ]
    """
    try:
        client = _get_gspread_client()
        sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
        worksheet = sheet.worksheet(settings.GOOGLE_SHEET_NAME)

        records = worksheet.get_all_records()
        logger.info("Fetched %d form responses from Google Sheets.", len(records))
        return records

    except FileNotFoundError:
        logger.error(
            "Credentials file not found: %s",
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
        )
        return []
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error("Spreadsheet with ID '%s' not found.", settings.GOOGLE_SHEET_ID)
        return []
    except Exception as exc:
        logger.exception("Unexpected error fetching Google Sheets data: %s", exc)
        return []
