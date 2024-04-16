SELECT t.Date
  ,c.location_id
  ,c.city
  ,c.latitude
  ,c.longitude
  ,t.MaxTemperature
  ,t.MinTemperature
  ,t.MaxApparentTemperature
  ,t.MinApparentTemperature
  ,t.AccumPrecipitation
fROM {{ ref('stg_temperatures') }} t
  INNER JOIN {{ ref('stg_cities') }} c ON c.location_id=t.location_id