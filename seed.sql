-- Sample fixed assets so the first run has something on the globe.
-- The service runs this only when query.sql is still the sample and geo.assets is missing.

CREATE DATABASE IF NOT EXISTS geo;

CREATE STABLE IF NOT EXISTS geo.assets (
  ts      TIMESTAMP,
  reading DOUBLE,
  status  VARCHAR(32)
) TAGS (
  asset_id  NCHAR(64),
  latitude  DOUBLE,
  longitude DOUBLE,
  height    DOUBLE
);

CREATE TABLE IF NOT EXISTS geo.pump_12 USING geo.assets TAGS ('PUMP-12', 38.6270, -90.1994, 12);
CREATE TABLE IF NOT EXISTS geo.tank_7  USING geo.assets TAGS ('TANK-7',  29.7604, -95.3698, 30);
CREATE TABLE IF NOT EXISTS geo.meter_4 USING geo.assets TAGS ('METER-4', 39.7392, -104.9903, 5);

INSERT INTO geo.pump_12 VALUES (NOW, 42.5, 'OK');
INSERT INTO geo.tank_7  VALUES (NOW, 88.0, 'ALARM');
INSERT INTO geo.meter_4 VALUES (NOW, 11.2, 'OK');
