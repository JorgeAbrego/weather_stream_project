SELECT DISTINCT location_id, latitude, longitude, elevation, city, timezone
FROM {{ source('staging','weather_staging') }}
ORDER BY 1