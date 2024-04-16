SELECT DATE(date) Date
  ,location_id 
  ,ROUND(MAX(temperature_2m),2) MaxTemperature
  ,ROUND(MIN(temperature_2m),2) MinTemperature
  ,ROUND(MAX(apparent_temperature),2) MaxApparentTemperature
  ,ROUND(MIN(apparent_temperature),2) MinApparentTemperature
  ,ROUND(SUM(precipitation),2) AccumPrecipitation
FROM {{ source('staging','weather_staging') }}
GROUP BY DATE(date), location_id