INSERT INTO nyc_311_requests (

    request_id,
    created_at,
    closed_at,
    agency,
    agency_name,
    complaint_type,
    descriptor,
    borough,
    city,
    status,
    latitude,
    longitude,
    resolution_hours,
    created_year,
    created_month,
    created_day,
    is_closed,
    ingested_at

)

SELECT

    request_id,
    created_at,
    closed_at,
    agency,
    agency_name,
    complaint_type,
    descriptor,
    borough,
    city,
    status,
    latitude,
    longitude,
    resolution_hours,
    created_year,
    created_month,
    created_day,
    is_closed,
    ingested_at

FROM staging_311_requests

ON CONFLICT (request_id)

DO UPDATE SET

    created_at = EXCLUDED.created_at,
    closed_at = EXCLUDED.closed_at,
    agency = EXCLUDED.agency,
    agency_name = EXCLUDED.agency_name,
    complaint_type = EXCLUDED.complaint_type,
    descriptor = EXCLUDED.descriptor,
    borough = EXCLUDED.borough,
    city = EXCLUDED.city,
    status = EXCLUDED.status,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    resolution_hours = EXCLUDED.resolution_hours,
    created_year = EXCLUDED.created_year,
    created_month = EXCLUDED.created_month,
    created_day = EXCLUDED.created_day,
    is_closed = EXCLUDED.is_closed,
    ingested_at = EXCLUDED.ingested_at;