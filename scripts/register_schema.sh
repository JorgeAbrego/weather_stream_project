#!/bin/bash

# Wait for Schema Registry to be available
echo "Waiting for Schema Registry..."
until $(curl --output /dev/null --silent --head --fail http://schema-registry:8081); do
    printf '.'
    sleep 5
done
echo "\nSchema Registry available."

# Register the schema
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     --data @/schema/weather_data.avsc \
     http://schema-registry:8081/subjects/jp-weather/versions

echo "Schema Registered."