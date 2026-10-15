-- cesium-tdengine:sample
-- One row per entity. Keep the aliases id, lon, lat, and height.
-- Replace this whole file to point the globe at your own tables.
-- See examples/fixed-assets.sql and examples/moving-fleet.sql.

SELECT
  LAST(ts)      AS ts,
  LAST(reading) AS reading,
  LAST(status)  AS status,
  asset_id      AS id,
  longitude     AS lon,
  latitude      AS lat,
  height
FROM geo.assets
GROUP BY tbname
