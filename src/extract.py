from pathlib import Path
from datetime import datetime, timedelta
import json

import requests

from database import get_connection


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

API_URL = (
    "https://data.cityofnewyork.us/"
    "resource/erm2-nwe9.json"
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# FIND INCREMENTAL START POINT
# ---------------------------------------------------------

def get_incremental_cutoff(
    overlap_hours=24
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT MAX(created_at)
                FROM nyc_311_requests;
                """
            )

            latest_date = (
                cursor.fetchone()[0]
            )


    # First run / empty database
    if latest_date is None:

        return (
            datetime.now()
            - timedelta(hours=overlap_hours)
        )


    # Re-fetch a small overlap window
    return (
        latest_date
        - timedelta(hours=overlap_hours)
    )


# ---------------------------------------------------------
# EXTRACT DATA WITH PAGINATION
# ---------------------------------------------------------

def extract_311_data(
    limit=1000,
    overlap_hours=24
):

    cutoff = get_incremental_cutoff(
        overlap_hours=overlap_hours
    )


    cutoff_string = cutoff.strftime(
        "%Y-%m-%dT%H:%M:%S.000"
    )


    print(
        f"Incremental cutoff: "
        f"{cutoff_string}"
    )


    all_records = []

    offset = 0
    page = 1


    while True:

        params = {

            "$select": """
                unique_key,
                created_date,
                closed_date,
                agency,
                agency_name,
                complaint_type,
                descriptor,
                borough,
                city,
                status,
                latitude,
                longitude
            """,

            "$where":
                f"created_date >= "
                f"'{cutoff_string}'",

            "$order":
                "created_date ASC, "
                "unique_key ASC",

            "$limit": limit,

            "$offset": offset
        }


        response = requests.get(
            API_URL,
            params=params,
            timeout=60
        )


        response.raise_for_status()

        batch = response.json()


        # No more records
        if not batch:
            break


        all_records.extend(
            batch
        )


        print(
            f"Page {page}: "
            f"{len(batch)} records"
        )


        # Last page
        if len(batch) < limit:
            break


        offset += limit
        page += 1


    return all_records


# ---------------------------------------------------------
# SAVE RAW DATA
# ---------------------------------------------------------

def save_raw_data(data):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


    file_path = (
        RAW_DIR
        / f"nyc_311_{timestamp}.json"
    )


    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


    return file_path


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n--- NYC 311 Incremental Extraction ---"
    )


    records = extract_311_data(
        limit=1000
    )


    file_path = save_raw_data(
        records
    )


    print(
        f"\nTotal records extracted: "
        f"{len(records)}"
    )


    print(
        f"Raw file saved: "
        f"{file_path}"
    )