import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_DIR / "src")
)


from validate import validate_data


def test_closed_before_created_is_rejected():

    df = pd.DataFrame(
        [
            {
                "request_id": 1001,
                "created_at": pd.Timestamp(
                    "2026-09-25 12:00:00"
                ),
                "closed_at": pd.Timestamp(
                    "2026-09-25 10:00:00"
                ),
                "agency": "DEP",
                "complaint_type": "Water Maintenance",
                "latitude": 40.7,
                "longitude": -73.9
            }
        ]
    )


    (
        valid_df,
        rejected_df,
        report
    ) = validate_data(df)


    assert len(valid_df) == 0

    assert len(rejected_df) == 1

    assert report["closed_before_created"] == 1


def test_missing_coordinates_are_warning_only():

    df = pd.DataFrame(
        [
            {
                "request_id": 1002,
                "created_at": pd.Timestamp(
                    "2026-09-25 12:00:00"
                ),
                "closed_at": pd.NaT,
                "agency": "DOT",
                "complaint_type": "Street Condition",
                "latitude": None,
                "longitude": None
            }
        ]
    )


    (
        valid_df,
        rejected_df,
        report
    ) = validate_data(df)


    assert len(valid_df) == 1

    assert len(rejected_df) == 0

    assert (
        report[
            "missing_coordinates_warning"
        ]
        == 1
    )