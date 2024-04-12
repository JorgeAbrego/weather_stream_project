from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

# Logger Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Schema Registry Configuration
schema_registry_url = "http://localhost:8081"
schema_registry_client = SchemaRegistryClient({'url': schema_registry_url})

# Get the schema for the specific topic
schema_metadata = schema_registry_client.get_latest_version("jp-weather")
schema_str = schema_metadata.schema.schema_str

# Initialize the AvroSerializer
avro_serializer = AvroSerializer(schema_str=schema_str, schema_registry_client=schema_registry_client)

producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': avro_serializer
}

producer = SerializingProducer(producer_conf)

class WeatherData(BaseModel):
    date_UTC: str
    temperature_2m: float
    relative_humidity_2m: float
    dew_point_2m: float
    apparent_temperature: float
    precipitation: float
    weather_code: int
    wind_speed_10m: float
    wind_speed_100m: float
    wind_direction_10m: float
    wind_direction_100m: float
    is_day: int
    sunshine_duration: float
    location_id: int
    latitude: float
    longitude: float
    elevation: float
    city: str
    timezone: str
    UtcOffsetSeconds: int
    date: str

@app.post("/weather/")
def send_weather_data(weather: WeatherData):
    try:
        # Convert the data to dictionary
        weather_dict = weather.dict()
        producer.produce(topic='jp-weather', key=str(weather.date_UTC), value=weather_dict)
        producer.flush()
        logger.info(f"Data sent for {weather.date_UTC}")
        return {"message": "Data sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send data")
