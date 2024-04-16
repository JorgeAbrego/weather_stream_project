import os
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
import pandas_gbq

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

PG_USER = os.getenv('POSTGRES_USER')
PG_PASS = os.getenv('POSTGRES_PASSWORD')
PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_NAME = os.getenv('DATASET_NAME')

def extract_data():
    filename = 'staging_file.csv'
    if os.path.exists(filename):
        os.remove(filename)
        print(f'Existing previous {filename} deleted.')
    engine = create_engine(f'postgresql+psycopg2://admindb:M4st3rP4ssw0rd.@postgres/staging_db')
    query = "SELECT DISTINCT * FROM weather_data"
    df = pd.read_sql(query, engine)
    df.to_csv(filename, index=False)
    engine.dispose()

def load_to_bigquery():
    filename = 'staging_file.csv'
    df = pd.read_csv(filename)
    df['date_UTC'] = pd.to_datetime(df['date_UTC'])
    df['date'] = pd.to_datetime(df['date'])
    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=f'{DATASET_NAME}.weather_staging',
        project_id=f'{PROJECT_ID}',
        if_exists='replace',
        table_schema=[
            {'name': 'key', 'type': 'INTEGER'},
            {'name': 'date_UTC', 'type': 'DATETIME'},
            {'name': 'temperature_2m', 'type': 'FLOAT'},
            {'name': 'relative_humidity_2m', 'type': 'FLOAT'},
            {'name': 'dew_point_2m', 'type': 'FLOAT'},
            {'name': 'apparent_temperature', 'type': 'FLOAT'},
            {'name': 'precipitation', 'type': 'FLOAT'},
            {'name': 'weather_code', 'type': 'INTEGER'},
            {'name': 'wind_speed_10m', 'type': 'FLOAT'},
            {'name': 'wind_speed_100m', 'type': 'FLOAT'},
            {'name': 'wind_direction_10m', 'type': 'FLOAT'},
            {'name': 'wind_direction_100m', 'type': 'FLOAT'},
            {'name': 'is_day', 'type': 'INTEGER'},
            {'name': 'sunshine_duration', 'type': 'FLOAT'},
            {'name': 'location_id', 'type': 'INTEGER'},
            {'name': 'latitude', 'type': 'FLOAT'},
            {'name': 'longitude', 'type': 'FLOAT'},
            {'name': 'elevation', 'type': 'FLOAT'},
            {'name': 'city', 'type': 'STRING'},
            {'name': 'timezone', 'type': 'STRING'},
            {'name': 'UtcOffsetSeconds', 'type': 'INTEGER'},
            {'name': 'date', 'type': 'DATETIME'}
        ]
    )
    
    
with DAG('postgres_to_bigquery',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    start = DummyOperator(task_id='start')

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    load_task = PythonOperator(
        task_id='load_to_bigquery',
        python_callable=load_to_bigquery
    )
    
    end = DummyOperator(task_id='end')

    start >> extract_task >> load_task >> end