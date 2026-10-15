-- Moving assets. Longitude and latitude are columns.

SELECT
  LAST(ts)        AS ts,
  LAST(longitude) AS lon,
  LAST(latitude)  AS lat,
  LAST(height)    AS height,
  LAST(speed)     AS speed,
  vehicle_id      AS id
FROM cesium_fleet.positions
GROUP BY tbname
