import os
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'description' : 'Dag to simulate streaming data from an API',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

def get_weather_data(ti, start_date, end_date):
    import openmeteo_requests
    import requests_cache
    import pandas as pd
    import numpy as np
    from retry_requests import retry
    from geopy.geocoders import Nominatim
    
    start_date = Variable.get("start_date")
    end_date = Variable.get("end_date")
    
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    geolocator = Nominatim(user_agent="VldApp061085")
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": [35.6766, 35.4657, 34.6924, 35.1845, 43.058, 33.5677, 38.2677, 34.9844, 35.8875, 34.4112],
        "longitude": [139.6911, 139.6154, 135.512, 136.9515, 141.4286, 130.3717, 140.8691, 135.7572, 139.6512, 132.4528],
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "weather_code", "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", "is_day", "sunshine_duration"],
        "timezone": "Asia/Tokyo"
    }
    responses = openmeteo.weather_api(url, params=params)
    
    df_list = []

    for response in responses:
        location = geolocator.reverse(str(response.Latitude())+","+str(response.Longitude()), language='en')
        address = location.raw['address']
        print(f"{address.get('city', '')} done")
        
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(3).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()
        hourly_wind_speed_100m = hourly.Variables(7).ValuesAsNumpy()
        hourly_wind_direction_10m = hourly.Variables(8).ValuesAsNumpy()
        hourly_wind_direction_100m = hourly.Variables(9).ValuesAsNumpy()
        hourly_is_day = hourly.Variables(10).ValuesAsNumpy()
        hourly_sunshine_duration = hourly.Variables(11).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["dew_point_2m"] = hourly_dew_point_2m
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
        hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
        hourly_data["wind_direction_100m"] = hourly_wind_direction_100m
        hourly_data["is_day"] = hourly_is_day
        hourly_data["sunshine_duration"] = hourly_sunshine_duration
        
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        hourly_dataframe['location_id'] = response.LocationId()
        hourly_dataframe['latitude'] = response.Latitude()
        hourly_dataframe['longitude'] = response.Longitude()
        hourly_dataframe['elevation'] = response.Elevation()
        hourly_dataframe['city'] = address.get('city', '')
        hourly_dataframe['timezone'] = response.TimezoneAbbreviation()
        hourly_dataframe['UtcOffsetSeconds'] = response.UtcOffsetSeconds()
        df_list.append(hourly_dataframe)
        
    df = pd.concat(df_list)
    destination_folder = 'data'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
    path = os.path.join(destination_folder, 'weather_data.csv')
    
    df_final = (df
                .rename(columns={'date':'date_UTC'})
                .assign(date=lambda x: x['date_UTC'].dt.tz_localize(None)+ pd.Timedelta(seconds=32400),
                        timezone=lambda x: x['timezone'].apply(lambda y: y.decode('utf-8')),
                        weather_code=lambda x: x['weather_code'].astype('int'),
                        is_day=lambda x: x['is_day'].astype('int'),
                        )
                ).to_csv(path, index=False)
    
    
def stream_to_kafka(ti):
    import pandas as pd
    import requests
    from time import sleep
    destination_folder = 'data'
    path = os.path.join(destination_folder, 'weather_data.csv')
    df = pd.read_csv(path)
    df['date_UTC'] = df['date_UTC'].astype(str)
    df['date'] = df['date'].astype(str)
    api_url = 'http://api-producer:8000/weather'
    for index, row in df.iterrows():
        data = row.to_dict()
        #print(data)
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            print(f'Data from row {index} was sent successfully')
        else:
            print(f'An error occurred trying sending data from row {index}: {response.text}')
        #sleep(2)

with DAG('weather_data_kafka',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    start = DummyOperator(task_id='start')

    get_data = PythonOperator(
        task_id='get_weather_data',
        python_callable=get_weather_data,
        op_kwargs={'start_date': '{{ var.value.start_date }}', 'end_date': '{{ var.value.end_date }}'}
    )

    stream = PythonOperator(
        task_id='stream_to_kafka',
        python_callable=stream_to_kafka
    )

    end = DummyOperator(task_id='end')

    start >> get_data >> stream >> end