# NYC 311 ETL Pipeline with Python and PostgreSQL

A local end-to-end ETL pipeline that extracts NYC 311 service-request data from the NYC Open Data API, transforms and validates the records, and loads them into PostgreSQL using a staging-to-curated database architecture.

The project was built to demonstrate practical data-engineering concepts including REST API ingestion, pagination, incremental extraction, data-quality validation, PostgreSQL bulk loading, UPSERT logic, idempotency, logging, automated testing, and SQL analytics.

---

## Pipeline Architecture

```text
NYC 311 Open Data API
        |
        v
Python Extraction
- REST API requests
- Pagination
- Incremental cutoff
- 24-hour overlap
        |
        v
Raw JSON
data/raw/
        |
        v
Transformation
- Data types
- Standardization
- Deduplication
- Derived fields
        |
        v
Validation
- Required fields
- Duplicate IDs
- Date logic
- Coordinate ranges
        |
        +--------------------+
        |                    |
        v                    v
Validated Data          Rejected Data
                              |
                              v
                       data/rejected/
        |
        v
PostgreSQL Staging Table
        |
        v
UPSERT
        |
        v
Curated PostgreSQL Table
        |
        v
SQL Analytics
```

---

## Tech Stack

**Languages:** Python, SQL

**Database:** PostgreSQL 17

**Python Libraries:** pandas, requests, psycopg, python-dotenv, pytest

**Tools:** VS Code, Git, GitHub

**Data Source:** NYC 311 Service Requests API

---

## Project Structure

```text
nyc-311-etl-pipeline/
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   ├── database.py
│   └── run_pipeline.py
│
├── sql/
│   ├── create_tables.sql
│   ├── upsert_requests.sql
│   └── analytics_queries.sql
│
├── tests/
│   ├── test_transform.py
│   └── test_validation.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── rejected/
│
├── logs/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Generated data files, logs, virtual environments, and local database credentials are excluded from Git through `.gitignore`.

---

## ETL Workflow

### Extract

`extract.py` connects to the NYC Open Data API and retrieves 311 service-request records.

The extractor supports pagination, requesting records in batches of 1,000 until the complete incremental dataset has been retrieved.

Instead of downloading the entire dataset on every run, the pipeline checks the most recent `created_at` timestamp stored in PostgreSQL.

A 24-hour overlap is applied to the extraction window so recently loaded requests can be retrieved again if their status or other fields have changed.

Existing records are safely handled later by PostgreSQL UPSERT logic.

### Transform

`transform.py` converts raw API records into an analytics-ready structure.

Transformations include:

- Renaming source fields
- Converting timestamps
- Converting latitude and longitude to numeric values
- Standardizing borough names
- Removing duplicate request IDs
- Calculating resolution time
- Creating year, month, and day fields
- Creating an `is_closed` indicator
- Adding an ingestion timestamp

### Validate

`validate.py` applies data-quality checks before records reach PostgreSQL.

Records are rejected when they contain issues such as:

- Missing request IDs
- Invalid creation timestamps
- Missing agency values
- Missing complaint types
- Duplicate request IDs
- Closure timestamps earlier than creation timestamps
- Invalid latitude or longitude ranges

Missing coordinates are recorded as a warning rather than causing the entire service request to be rejected.

Rejected records are preserved separately for investigation.

### Load

Validated records are first bulk-loaded into:

```text
staging_311_requests
```

PostgreSQL `COPY` is used for efficient batch loading.

Records are then moved into:

```text
nyc_311_requests
```

using:

```sql
ON CONFLICT (request_id)
DO UPDATE
```

This makes the load idempotent.

If a request already exists, its information is updated. If the request is new, it is inserted.

Running the same batch repeatedly therefore does not create duplicate service requests.

---

## Database Design

The project uses two PostgreSQL tables.

```text
staging_311_requests
```

acts as a temporary landing table for each incoming batch.

```text
nyc_311_requests
```

is the permanent curated table used for analytics.

`request_id` is the primary key of the curated table.

Indexes are created on:

```text
created_at
complaint_type
borough
```

to improve common analytical queries.

---

## Data Quality

During one pipeline validation run:

```text
Extracted records:        11,050
Valid records:            11,047
Rejected records:              3
Missing coordinates:         185
```

The three rejected records contained closure timestamps earlier than their creation timestamps and were preserved separately instead of being silently discarded.

After loading overlapping API batches, the database contained:

```text
Total records:            12,039
Unique request IDs:       12,039
```

confirming that the UPSERT logic prevented duplicate request IDs.

---

## Example Analytics

The included SQL queries analyze:

```text
Total service requests
Requests by borough
Top complaint types
Requests by agency
Open vs. closed requests
Average resolution time by agency
Daily request volume
Database quality metrics
```

Example results from the local dataset included:

```text
Total requests: 12,039

Top boroughs:
Brooklyn       3,744
Queens         3,076
Manhattan      2,549
Bronx          2,161
Staten Island    492

Top complaint:
Illegal Parking — 2,015 requests
```

---

## Logging

Every complete pipeline execution writes operational information to:

```text
logs/pipeline.log
```

The log records:

```text
Pipeline start
Extraction volume
Transformation results
Validation results
Rejected rows
Database load counts
Successful completion
Errors and stack traces
```

This provides a basic audit trail for pipeline execution and troubleshooting.

---

## Automated Tests

The project uses `pytest` to test transformation and validation behavior.

Current tests verify that:

```text
Transformation correctly standardizes and derives fields
Invalid date sequences are rejected
Missing coordinates remain valid but generate warnings
```

Run the test suite with:

```bash
pytest -v
```

Current result:

```text
3 passed
```

---

## Setup

Clone the repository and create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a PostgreSQL database:

```bash
createdb nyc_311
```

Create the database tables:

```bash
psql nyc_311 -f sql/create_tables.sql
```

Create a `.env` file based on `.env.example`:

```text
DB_NAME=nyc_311
DB_USER=your_postgres_username
```

---

## Run the Pipeline

Execute the complete ETL workflow with:

```bash
python src/run_pipeline.py
```

This runs:

```text
Extract
   ↓
Transform
   ↓
Validate
   ↓
Load
```

in one command.

---

## Run Analytics

Execute the SQL analytics queries with:

```bash
psql nyc_311 -f sql/analytics_queries.sql
```

---

## Key Engineering Concepts Demonstrated

```text
REST API ingestion
API pagination
Incremental extraction
Overlap-based record refresh
Raw data preservation
Data transformation
Data validation
Rejected-record handling
PostgreSQL staging tables
Bulk loading with COPY
UPSERT / conflict handling
Idempotent pipelines
Database indexing
Environment-variable configuration
Logging and error handling
Automated testing
SQL analytics
```

---

## Author

Aastha Chavan  
MS Business Analytics — Brandeis University