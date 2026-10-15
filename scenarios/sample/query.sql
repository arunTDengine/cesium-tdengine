-- cesium-tdengine:sample
-- Fixed assets. One child table is one point on the globe.

SELECT
  LAST(ts)      AS ts,
  LAST(reading) AS reading,
  LAST(status)  AS status,
  asset_id      AS id,
  longitude     AS lon,
  latitude      AS lat,
  height
FROM cesium_sample.assets
GROUP BY tbname
