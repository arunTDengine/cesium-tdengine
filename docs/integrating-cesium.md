# Connecting CesiumJS

CesiumJS draws the globe. TDengine stores the time series. There is no plugin. This package is the connection: a short Python service reads taosAdapter and the page draws one entity per asset.

It is not tied to one plant or one schema. A wind farm, a fleet, a pipeline, and a set of fixed sensors all use the same service. You change `query.sql`.

```text
CesiumJS page
    GET /api/assets
        |
server.py          password stays here
    POST /rest/sql
        |
taosAdapter -> TDengine
```

## Get started

Python 3.9 or later. TDengine 3.x with taosAdapter. No extra Python packages.

```bash
git clone https://origin.cursor.com/arun-arulraj/cesium-tdengine.git
cd cesium-tdengine
python3 server.py
```

Open http://127.0.0.1:8095/

Defaults are `http://localhost:6041/rest/sql`, user `root`, password `taosdata`. If `query.sql` is still the sample and the table is missing, the first request creates database `geo` and three assets so the globe is not empty.

```bash
export TAOS_URL=http://localhost:6041/rest/sql
export TAOS_USER=root
export TAOS_PASSWORD=taosdata
python3 server.py
```

## Point it at your tables

`query.sql` must return `id`, `lon`, `lat`, and `height`. Other columns are optional. They show up when an operator clicks a point.

Fixed assets keep longitude and latitude in tags. One child table is one entity:

```sql
SELECT LAST(ts) AS ts, LAST(active_power) AS power, LAST(status) AS status,
       turbine_id AS id, longitude AS lon, latitude AS lat, 80 AS height
FROM wind.turbines
GROUP BY tbname
```

Moving assets keep longitude and latitude in columns:

```sql
SELECT LAST(ts) AS ts, LAST(longitude) AS lon, LAST(latitude) AS lat,
       LAST(height) AS height, LAST(speed) AS speed, vehicle_id AS id
FROM fleet.positions
GROUP BY tbname
```

Those two queries are also in `examples/`. Copy one over `query.sql` and rename the columns. Remove the line `-- cesium-tdengine:sample` so the sample seed does not run against your server.

Alias every `LAST()` you want in the JSON. `LAST(longitude)` without `AS lon` comes back as `last(longitude)`, and the page ignores it.

Cesium expects longitude, then latitude, then height in meters.

## Tracks

Copy `examples/track.sql` to `track.sql` when an asset moves and you want the path, not only the latest point. `{id}` is filled from `GET /api/track?id=VAN-4`. Keep `INTERVAL` in that query so a long history stays small.

## TDengine IDMP

If the assets are already IDMP elements, leave the page as it is and read attributes in the service instead of SQL.

1. Log in with `POST /api/v1/users/login` and send the token on later calls.
2. List the children of the parent element.
3. Cache attribute ids.
4. Read current values and return the same JSON: `id`, `lon`, `lat`, `height`, plus measurements.

Coordinates come from the element location or from a lookup in the service. Embed the page in an IDMP dashboard with an iframe pointed at `http://127.0.0.1:8095/`. See [Embedding Panels and Dashboards](https://idmpdocs.tdengine.com/integrating-with-other-systems/).

## Troubleshooting

| What you see | What it usually is |
|---|---|
| Connection error on the page | taosAdapter is not at `TAOS_URL`, or the user and password are wrong. |
| Empty asset list | No child tables, or latitude and longitude are null. |
| Blank globe | The HTML file was opened directly. Use the URL printed by `server.py`. |
| Point in the wrong place | `lon` and `lat` are reversed. |
| Duplicate or jumping points | `id` is not stable across polls. Use the asset id, not the timestamp. |
