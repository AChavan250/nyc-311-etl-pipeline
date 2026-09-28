import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_DIR / "src")
)


from transform import transform_data


def test_transform_data():

    raw_data = pd.DataFrame(
        [
            {
                "unique_key": "1001",
                "created_date": "2026-09-25T10:00:00",
                "closed_date": "2026-09-25T12:00:00",
                "agency": "NYPD",
                "agency_name": "Police Department",
                "complaint_type": "Noise",
                "descriptor": "Loud Music",
                "borough": "brooklyn",
                "city": "Brooklyn",
                "status": "Closed",
                "latitude": "40.65",
                "longitude": "-73.95"
            }
        ]
    )


    (
        clean_df,
        original_rows,
        duplicates_removed
    ) = transform_data(raw_data)


    assert original_rows == 1

    assert len(clean_df) == 1

    assert duplicates_removed == 0

    assert clean_df.iloc[0]["request_id"] == 1001

    assert clean_df.iloc[0]["borough"] == "BROOKLYN"

    assert clean_df.iloc[0]["resolution_hours"] == 2.0

    assert clean_df.iloc[0]["is_closed"] == True