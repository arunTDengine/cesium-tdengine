CREATE DATABASE IF NOT EXISTS cesium_fleet;

CREATE STABLE IF NOT EXISTS cesium_fleet.positions (
  ts        TIMESTAMP,
  latitude  DOUBLE,
  longitude DOUBLE,
  height    DOUBLE,
  speed     DOUBLE
) TAGS (
  vehicle_id NCHAR(64)
);

CREATE TABLE IF NOT EXISTS cesium_fleet.van_4  USING cesium_fleet.positions TAGS ('VAN-4');
CREATE TABLE IF NOT EXISTS cesium_fleet.ship_2 USING cesium_fleet.positions TAGS ('SHIP-2');

INSERT INTO cesium_fleet.van_4  VALUES (NOW, 37.7749, -122.4194, 10, 18.0);
INSERT INTO cesium_fleet.ship_2 VALUES (NOW, 40.7128, -74.0060, 5, 12.4);
