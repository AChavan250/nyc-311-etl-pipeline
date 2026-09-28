from pathlib import Path
import json

import pandas as pd


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# FIND MOST RECENT RAW FILE
# ---------------------------------------------------------

def get_latest_raw_file():

    files = list(
        RAW_DIR.glob("nyc_311_*.json")
    )

    if not files:
        raise FileNotFoundError(
            "No raw NYC 311 files found."
        )

    return max(
        files,
        key=lambda file: file.stat().st_mtime
    )


# ---------------------------------------------------------
# LOAD RAW DATA
# ---------------------------------------------------------

def load_raw_data(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return pd.DataFrame(data)


# ---------------------------------------------------------
# TRANSFORM DATA
# ---------------------------------------------------------

def transform_data(df):

    df = df.copy()

    original_rows = len(df)


    # -----------------------------
    # Rename columns
    # -----------------------------

    df = df.rename(
        columns={
            "unique_key": "request_id",
            "created_date": "created_at",
            "closed_date": "closed_at"
        }
    )


    # -----------------------------
    # Clean string columns
    # -----------------------------

    text_columns = [
        "agency",
        "agency_name",
        "complaint_type",
        "descriptor",
        "borough",
        "city",
        "status"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )


    # -----------------------------
    # Standardize borough
    # -----------------------------

    if "borough" in df.columns:

        df["borough"] = (
            df["borough"]
            .str.upper()
        )


    # -----------------------------
    # Convert dates
    # -----------------------------

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df["closed_at"] = pd.to_datetime(
        df["closed_at"],
        errors="coerce"
    )


    # -----------------------------
    # Convert coordinates
    # -----------------------------

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )


    # -----------------------------
    # Convert request ID
    # -----------------------------

    df["request_id"] = pd.to_numeric(
        df["request_id"],
        errors="coerce"
    ).astype("Int64")


    # -----------------------------
    # Remove duplicate requests
    # -----------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=["request_id"],
        keep="first"
    )

    duplicates_removed = (
        before_dedup - len(df)
    )


    # -----------------------------
    # Derived fields
    # -----------------------------

    df["resolution_hours"] = (
        (
            df["closed_at"]
            - df["created_at"]
        )
        .dt.total_seconds()
        / 3600
    )


    # Negative resolution times are invalid
    df.loc[
        df["resolution_hours"] < 0,
        "resolution_hours"
    ] = pd.NA


    df["created_year"] = (
        df["created_at"].dt.year
    )

    df["created_month"] = (
        df["created_at"].dt.month
    )

    df["created_day"] = (
        df["created_at"].dt.day
    )


    df["is_closed"] = (
        df["closed_at"].notna()
    )


    # -----------------------------
    # Add ETL timestamp
    # -----------------------------

    df["ingested_at"] = (
        pd.Timestamp.now()
    )


    # -----------------------------
    # Final column order
    # -----------------------------

    columns = [
        "request_id",
        "created_at",
        "closed_at",
        "agency",
        "agency_name",
        "complaint_type",
        "descriptor",
        "borough",
        "city",
        "status",
        "latitude",
        "longitude",
        "resolution_hours",
        "created_year",
        "created_month",
        "created_day",
        "is_closed",
        "ingested_at"
    ]

    df = df[columns]


    return (
        df,
        original_rows,
        duplicates_removed
    )


# ---------------------------------------------------------
# SAVE PROCESSED DATA
# ---------------------------------------------------------

def save_processed_data(
    df,
    raw_file
):

    timestamp = (
        raw_file
        .stem
        .replace(
            "nyc_311_",
            ""
        )
    )

    output_file = (
        PROCESSED_DIR
        / f"nyc_311_clean_{timestamp}.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    return output_file


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n--- NYC 311 Transformation ---"
    )

    raw_file = get_latest_raw_file()

    raw_df = load_raw_data(
        raw_file
    )

    (
        clean_df,
        original_rows,
        duplicates_removed
    ) = transform_data(
        raw_df
    )

    output_file = save_processed_data(
        clean_df,
        raw_file
    )


    print(
        f"Input rows: {original_rows}"
    )

    print(
        f"Output rows: {len(clean_df)}"
    )

    print(
        f"Duplicates removed: "
        f"{duplicates_removed}"
    )

    print(
        f"Missing request IDs: "
        f"{clean_df['request_id'].isna().sum()}"
    )

    print(
        f"Invalid created dates: "
        f"{clean_df['created_at'].isna().sum()}"
    )

    print(
        f"Processed file saved: "
        f"{output_file}"
    )


    print(
        "\nSample transformed record:"
    )

    print(
        clean_df.head(1)
        .to_string(index=False)
    )