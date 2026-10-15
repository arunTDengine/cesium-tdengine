-- Moving assets: a vehicle, drone, ship, or person.
-- Longitude and latitude are columns, because the coordinate is the time series.
-- This query is the live dot. For the path, use examples/track.sql.

SELECT
  LAST(ts)        AS ts,
  LAST(longitude) AS lon,
  LAST(latitude)  AS lat,
  LAST(height)    AS height,
  LAST(speed)     AS speed,
  vehicle_id      AS id
FROM fleet.positions
GROUP BY tbname
