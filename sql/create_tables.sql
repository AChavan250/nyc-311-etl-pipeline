CREATE TABLE IF NOT EXISTS staging_311_requests (

    request_id BIGINT,
    created_at TIMESTAMP,
    closed_at TIMESTAMP,

    agency TEXT,
    agency_name TEXT,
    complaint_type TEXT,
    descriptor TEXT,

    borough TEXT,
    city TEXT,
    status TEXT,

    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    resolution_hours DOUBLE PRECISION,

    created_year INTEGER,
    created_month INTEGER,
    created_day INTEGER,

    is_closed BOOLEAN,

    ingested_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS nyc_311_requests (

    request_id BIGINT PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,

    agency TEXT NOT NULL,
    agency_name TEXT,
    complaint_type TEXT NOT NULL,
    descriptor TEXT,

    borough TEXT,
    city TEXT,
    status TEXT,

    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    resolution_hours DOUBLE PRECISION,

    created_year INTEGER,
    created_month INTEGER,
    created_day INTEGER,

    is_closed BOOLEAN,

    ingested_at TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_311_created_at
ON nyc_311_requests(created_at);


CREATE INDEX IF NOT EXISTS idx_311_complaint_type
ON nyc_311_requests(complaint_type);


CREATE INDEX IF NOT EXISTS idx_311_borough
ON nyc_311_requests(borough);