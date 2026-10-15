CREATE DATABASE IF NOT EXISTS cesium_sample;

CREATE STABLE IF NOT EXISTS cesium_sample.assets (
  ts      TIMESTAMP,
  reading DOUBLE,
  status  VARCHAR(32)
) TAGS (
  asset_id  NCHAR(64),
  latitude  DOUBLE,
  longitude DOUBLE,
  height    DOUBLE
);

CREATE TABLE IF NOT EXISTS cesium_sample.pump_12 USING cesium_sample.assets TAGS ('PUMP-12', 38.6270, -90.1994, 12);
CREATE TABLE IF NOT EXISTS cesium_sample.tank_7  USING cesium_sample.assets TAGS ('TANK-7',  29.7604, -95.3698, 30);
CREATE TABLE IF NOT EXISTS cesium_sample.meter_4 USING cesium_sample.assets TAGS ('METER-4', 39.7392, -104.9903, 5);

INSERT INTO cesium_sample.pump_12 VALUES (NOW, 42.5, 'OK');
INSERT INTO cesium_sample.tank_7  VALUES (NOW, 88.0, 'ALARM');
INSERT INTO cesium_sample.meter_4 VALUES (NOW, 11.2, 'OK');
