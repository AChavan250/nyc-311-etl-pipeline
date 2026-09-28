from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_DIR / ".env")


def get_connection():

    connection = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER")
    )

    return connection