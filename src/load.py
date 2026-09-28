from pathlib import Path

from database import get_connection


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

UPSERT_FILE = (
    PROJECT_DIR
    / "sql"
    / "upsert_requests.sql"
)


# ---------------------------------------------------------
# FIND LATEST VALIDATED FILE
# ---------------------------------------------------------

def get_latest_validated_file():

    files = list(
        PROCESSED_DIR.glob(
            "nyc_311_validated_*.csv"
        )
    )

    if not files:
        raise FileNotFoundError(
            "No validated NYC 311 file found."
        )

    return max(
        files,
        key=lambda file: file.stat().st_mtime
    )


# ---------------------------------------------------------
# LOAD DATA INTO POSTGRESQL
# ---------------------------------------------------------

def load_to_postgres(csv_file):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # Clear previous staging batch
            cursor.execute(
                "TRUNCATE TABLE staging_311_requests;"
            )


            # Load CSV into staging table
            with open(
                csv_file,
                "r",
                encoding="utf-8"
            ) as file:

                with cursor.copy(
                    """
                    COPY staging_311_requests
                    FROM STDIN
                    WITH (
                        FORMAT CSV,
                        HEADER TRUE
                    )
                    """
                ) as copy:

                    while data := file.read(8192):
                        copy.write(data)


            # Count staging rows
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM staging_311_requests;
                """
            )

            staging_count = (
                cursor.fetchone()[0]
            )


            # Read UPSERT SQL
            with open(
                UPSERT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                upsert_sql = file.read()


            # Move staging data into main table
            cursor.execute(
                upsert_sql
            )


            # Count permanent records
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM nyc_311_requests;
                """
            )

            total_count = (
                cursor.fetchone()[0]
            )


    return staging_count, total_count


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n--- NYC 311 PostgreSQL Load ---"
    )

    validated_file = (
        get_latest_validated_file()
    )

    print(
        f"Loading file: "
        f"{validated_file}"
    )


    (
        staging_count,
        total_count
    ) = load_to_postgres(
        validated_file
    )


    print(
        f"Rows loaded to staging: "
        f"{staging_count}"
    )

    print(
        f"Total rows in main table: "
        f"{total_count}"
    )

    print(
        "Database load completed successfully."
    )