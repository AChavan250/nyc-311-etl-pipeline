from pathlib import Path
import logging

from extract import extract_311_data, save_raw_data

from transform import (
    load_raw_data,
    transform_data,
    save_processed_data
)

from validate import (
    load_processed_data,
    validate_data,
    save_validation_results
)

from load import load_to_postgres


# ---------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


logging.basicConfig(
    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),

    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------

def run_pipeline():

    logger.info(
        "================================"
    )

    logger.info(
        "NYC 311 ETL PIPELINE STARTED"
    )

    logger.info(
        "================================"
    )


    try:

        # -------------------------------------------------
        # EXTRACT
        # -------------------------------------------------

        logger.info(
            "[1/4] Extracting data"
        )

        records = extract_311_data(
            limit=1000
        )

        raw_file = save_raw_data(
            records
        )

        logger.info(
            f"Extracted records: "
            f"{len(records)}"
        )

        logger.info(
            f"Raw file: {raw_file}"
        )


        # -------------------------------------------------
        # TRANSFORM
        # -------------------------------------------------

        logger.info(
            "[2/4] Transforming data"
        )

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

        clean_file = save_processed_data(
            clean_df,
            raw_file
        )

        logger.info(
            f"Input rows: {original_rows}"
        )

        logger.info(
            f"Clean rows: {len(clean_df)}"
        )

        logger.info(
            f"Duplicates removed: "
            f"{duplicates_removed}"
        )


        # -------------------------------------------------
        # VALIDATE
        # -------------------------------------------------

        logger.info(
            "[3/4] Validating data"
        )

        processed_df = load_processed_data(
            clean_file
        )

        (
            valid_df,
            rejected_df,
            report
        ) = validate_data(
            processed_df
        )

        (
            validated_file,
            rejected_file,
            report_file
        ) = save_validation_results(
            valid_df,
            rejected_df,
            report,
            clean_file
        )

        logger.info(
            f"Valid rows: "
            f"{report['valid_rows']}"
        )

        logger.info(
            f"Rejected rows: "
            f"{report['rejected_rows']}"
        )

        logger.info(
            f"Missing coordinates: "
            f"{report['missing_coordinates_warning']}"
        )


        # -------------------------------------------------
        # LOAD
        # -------------------------------------------------

        logger.info(
            "[4/4] Loading into PostgreSQL"
        )

        (
            staging_count,
            total_count
        ) = load_to_postgres(
            validated_file
        )

        logger.info(
            f"Rows loaded to staging: "
            f"{staging_count}"
        )

        logger.info(
            f"Total database rows: "
            f"{total_count}"
        )


        logger.info(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )


    except Exception:

        logger.exception(
            "PIPELINE FAILED"
        )

        raise


if __name__ == "__main__":

    run_pipeline()