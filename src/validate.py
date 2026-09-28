from pathlib import Path
import json

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
REJECTED_DIR = PROJECT_DIR / "data" / "rejected"

REJECTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def get_latest_processed_file():

    files = list(
        PROCESSED_DIR.glob(
            "nyc_311_clean_*.csv"
        )
    )

    if not files:
        raise FileNotFoundError(
            "No processed NYC 311 files found."
        )

    return max(
        files,
        key=lambda file: file.stat().st_mtime
    )


def load_processed_data(file_path):

    df = pd.read_csv(file_path)

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df["closed_at"] = pd.to_datetime(
        df["closed_at"],
        errors="coerce"
    )

    return df


def validate_data(df):

    df = df.copy()

    required_columns = [
        "request_id",
        "created_at",
        "agency",
        "complaint_type",
        "latitude",
        "longitude"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


    df["validation_errors"] = ""


    def add_error(mask, message):

        df.loc[
            mask,
            "validation_errors"
        ] += message + "; "


    missing_request_id = (
        df["request_id"].isna()
    )

    add_error(
        missing_request_id,
        "missing_request_id"
    )


    invalid_created_date = (
        df["created_at"].isna()
    )

    add_error(
        invalid_created_date,
        "invalid_created_date"
    )


    missing_agency = (
        df["agency"].isna()
        | (
            df["agency"]
            .astype(str)
            .str.strip()
            == ""
        )
    )

    add_error(
        missing_agency,
        "missing_agency"
    )


    missing_complaint_type = (
        df["complaint_type"].isna()
        | (
            df["complaint_type"]
            .astype(str)
            .str.strip()
            == ""
        )
    )

    add_error(
        missing_complaint_type,
        "missing_complaint_type"
    )


    duplicate_request_id = (
        df["request_id"].duplicated(
            keep=False
        )
    )

    add_error(
        duplicate_request_id,
        "duplicate_request_id"
    )


    closed_before_created = (
        df["closed_at"].notna()
        & df["created_at"].notna()
        & (
            df["closed_at"]
            < df["created_at"]
        )
    )

    add_error(
        closed_before_created,
        "closed_before_created"
    )


    invalid_latitude = (
        df["latitude"].notna()
        & ~df["latitude"].between(
            -90,
            90
        )
    )

    add_error(
        invalid_latitude,
        "invalid_latitude"
    )


    invalid_longitude = (
        df["longitude"].notna()
        & ~df["longitude"].between(
            -180,
            180
        )
    )

    add_error(
        invalid_longitude,
        "invalid_longitude"
    )


    df["validation_errors"] = (
        df["validation_errors"]
        .str.rstrip("; ")
    )


    valid_df = df[
        df["validation_errors"] == ""
    ].copy()


    rejected_df = df[
        df["validation_errors"] != ""
    ].copy()


    valid_df = valid_df.drop(
        columns=["validation_errors"]
    )


    missing_coordinates = (
        df["latitude"].isna()
        | df["longitude"].isna()
    )


    report = {

        "input_rows": len(df),

        "valid_rows": len(valid_df),

        "rejected_rows": len(rejected_df),

        "missing_request_ids":
            int(missing_request_id.sum()),

        "duplicate_request_ids":
            int(duplicate_request_id.sum()),

        "invalid_created_dates":
            int(invalid_created_date.sum()),

        "missing_agency":
            int(missing_agency.sum()),

        "missing_complaint_type":
            int(missing_complaint_type.sum()),

        "closed_before_created":
            int(closed_before_created.sum()),

        "invalid_latitudes":
            int(invalid_latitude.sum()),

        "invalid_longitudes":
            int(invalid_longitude.sum()),

        "missing_coordinates_warning":
            int(missing_coordinates.sum())
    }


    return (
        valid_df,
        rejected_df,
        report
    )


def save_validation_results(
    valid_df,
    rejected_df,
    report,
    source_file
):

    timestamp = (
        source_file
        .stem
        .replace(
            "nyc_311_clean_",
            ""
        )
    )


    valid_file = (
        PROCESSED_DIR
        / f"nyc_311_validated_{timestamp}.csv"
    )


    rejected_file = (
        REJECTED_DIR
        / f"nyc_311_rejected_{timestamp}.csv"
    )


    report_file = (
        PROCESSED_DIR
        / f"validation_report_{timestamp}.json"
    )


    valid_df.to_csv(
        valid_file,
        index=False
    )


    if len(rejected_df) > 0:

        rejected_df.to_csv(
            rejected_file,
            index=False
        )


    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )


    return (
        valid_file,
        rejected_file,
        report_file
    )


if __name__ == "__main__":

    print(
        "\n--- NYC 311 Validation ---"
    )


    processed_file = (
        get_latest_processed_file()
    )


    df = load_processed_data(
        processed_file
    )


    (
        valid_df,
        rejected_df,
        report
    ) = validate_data(
        df
    )


    (
        valid_file,
        rejected_file,
        report_file
    ) = save_validation_results(
        valid_df,
        rejected_df,
        report,
        processed_file
    )


    print(
        f"Input rows: "
        f"{report['input_rows']}"
    )

    print(
        f"Valid rows: "
        f"{report['valid_rows']}"
    )

    print(
        f"Rejected rows: "
        f"{report['rejected_rows']}"
    )

    print(
        f"Missing coordinates "
        f"(warning only): "
        f"{report['missing_coordinates_warning']}"
    )

    print(
        f"Validated file saved: "
        f"{valid_file}"
    )

    print(
        f"Validation report saved: "
        f"{report_file}"
    )