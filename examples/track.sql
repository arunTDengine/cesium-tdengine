-- Path for one moving asset.
-- Copy this file to track.sql next to server.py to turn on GET /api/track?id=
-- {id} is replaced with the asset id from the query string.

SELECT
  _wstart         AS ts,
  LAST(longitude) AS lon,
  LAST(latitude)  AS lat,
  LAST(height)    AS height
FROM fleet.positions
WHERE vehicle_id = '{id}' AND ts >= NOW - 6h
INTERVAL(30s)
