-- Fixed assets: a site, turbine, well, building, or meter.
-- Longitude and latitude are tags. They do not change on every insert.
-- One child table is one entity.

SELECT
  LAST(ts)           AS ts,
  LAST(active_power) AS power,
  LAST(status)       AS status,
  turbine_id         AS id,
  longitude          AS lon,
  latitude           AS lat,
  80                 AS height
FROM wind.turbines
GROUP BY tbname
