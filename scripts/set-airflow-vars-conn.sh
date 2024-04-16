#!/bin/bash

# Wait until Airflow is ready
airflow db check

airflow variables set start_date "2024-01-01"

airflow variables set end_date "2024-03-31"

# Create connection to Google Cloud
airflow connections add 'google_cloud_default' \
    --conn-type 'google_cloud_platform' \
    --conn-extra '{
        "extra__google_cloud_platform__project": ${GCP_PROJECT_ID},
        "extra__google_cloud_platform__key_path": ${GOOGLE_APPLICATION_CREDENTIALS}
    }'