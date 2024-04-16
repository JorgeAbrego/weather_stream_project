from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer
import json
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()

# Define the data model using Pydantic for automatic validation
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

# Kafka Producer Configuration
producer = KafkaProducer(
    bootstrap_servers=['broker:29092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.post("/weather/")
async def send_data(weather_data: WeatherData):
    try:
        # Send data to Kafka topic
        value=weather_data.dict()
        key=f"{value['date'].replace('-','').replace(' ','').replace(':', '')[:14]}{value['location_id']:03d}".encode('utf-8')
        producer.send('jp-weather', key=key, value=value)
        producer.flush()
        logging.info("Data sent to Kafka successfully")
        return {"message": "Data sent to Kafka successfully"}
    except Exception as e:
        logging.error(f"Failed to send data to Kafka: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))