from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import *

# Create the Spark session
spark = SparkSession.builder \
    .appName("KafkaWeatherConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1") \
    .master("local[*]") \
    .getOrCreate()

# Define the data schema
schema = StructType([
    StructField("date_UTC", StringType()),
    StructField("temperature_2m", DoubleType()),
    StructField("relative_humidity_2m", DoubleType()),
    StructField("dew_point_2m", DoubleType()),
    StructField("apparent_temperature", DoubleType()),
    StructField("precipitation", DoubleType()),
    StructField("weather_code", IntegerType()),
    StructField("wind_speed_10m", DoubleType()),
    StructField("wind_speed_100m", DoubleType()),
    StructField("wind_direction_10m", DoubleType()),
    StructField("wind_direction_100m", DoubleType()),
    StructField("is_day", IntegerType()),
    StructField("sunshine_duration", DoubleType()),
    StructField("location_id", IntegerType()),
    StructField("latitude", DoubleType()),
    StructField("longitude", DoubleType()),
    StructField("elevation", DoubleType()),
    StructField("city", StringType()),
    StructField("timezone", StringType()),
    StructField("UtcOffsetSeconds", IntegerType()),
    StructField("date", StringType())
])

kafka_topic = "jp-weather"
kafka_bootstrap_servers = "broker:29092"  # Adjust according to your settings

kafka_properties = {
    "kafka.bootstrap.servers": kafka_bootstrap_servers,
    "subscribe": kafka_topic,
    "startingOffsets": "earliest"  # It can be "latest" if you are only interested in new messages
}

df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_properties) \
    .load()

df = df.select(
    col("key").cast("string").alias("key"),
    from_json(col("value").cast("string"), schema).alias("data")
).select("key", "data.*")

# Show data in console for debugging
query = df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()