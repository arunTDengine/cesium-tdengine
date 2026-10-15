# CesiumJS and TDengine

Clone this repository, point it at TDengine, and open the globe. The same package works for a wind farm, a vehicle fleet, a plant, or any other scene. You change one SQL file.

The browser never sees the database password.

## Run

You need Python 3.9 or later and TDengine 3.x with taosAdapter. Nothing to install with pip. CesiumJS loads from the Cesium CDN.

```bash
python3 server.py
```

Open http://127.0.0.1:8095/

The default connection is `http://localhost:6041/rest/sql` as `root` / `taosdata`. On the first request, if `query.sql` is still the sample and `geo.assets` does not exist, the service creates that database and three assets: PUMP-12, TANK-7, and METER-4. The globe flies to them.

Use your own host, user, or port when the defaults are wrong:

```bash
export TAOS_URL=http://localhost:6041/rest/sql
export TAOS_USER=root
export TAOS_PASSWORD=taosdata
export PORT=8095
python3 server.py
```

Check the database on its own if the page shows a connection error:

```bash
curl -sS -u root:taosdata -d "SELECT SERVER_VERSION()" http://localhost:6041/rest/sql
```

A healthy response contains `"code":0`.

## Use your own assets

Edit `query.sql`. Keep the aliases `id`, `lon`, `lat`, and `height`. Any other column you select is passed through and shown when someone clicks a point. Delete the line `-- cesium-tdengine:sample` when you leave the sample, so a typo cannot create the `geo` database.

| Scene | Where longitude and latitude go | Query shape |
|---|---|---|
| Site, turbine, building, well, meter | Tags. The asset does not move. | `LAST()` of the measurements, `GROUP BY tbname`. One child table is one point. |
| Vehicle, drone, ship, person | Columns, next to `ts`. Only the id is a tag. | `LAST(longitude)` and `LAST(latitude)` for the live dot. |

`examples/fixed-assets.sql` and `examples/moving-fleet.sql` are the two shapes. Copy the one you need over `query.sql` and change the table and column names.

`GROUP BY tbname` returns one row per child table. Alias `LAST(longitude)` as `lon`. Without the alias, the JSON key is `last(longitude)` and the page skips the row.

Cesium takes longitude first. If a point lands in the ocean, `lon` and `lat` are swapped.

## A moving path

`/api/assets` is the latest position. A path is a second query.

```bash
cp examples/track.sql track.sql
```

Edit the table name, then open `GET /api/track?id=VAN-4`. `{id}` in that file is replaced with the query-string id. `INTERVAL` downsamples the track so the browser does not receive every raw row. Build a `SampledPositionProperty` from `samples` if you want Cesium to draw the trail. The included page draws the latest point.

## IDMP instead of SQL

When the assets are already elements in TDengine IDMP, keep this page and swap the reader inside `server.py`. IDMP attributes are already bound to TDengine columns.

1. `POST /api/v1/users/login` and keep the token.
2. `GET /api/v1/elements?parentId=<id>&size=200` for the children that belong on the globe.
3. Cache attribute ids from `GET /api/v1/elements/<id>/attributes`.
4. `POST /api/v1/elements/<id>/attributes/data` with those ids.

Return the same list: `id`, `lon`, `lat`, `height`, then whatever measurements the click card should show. Take coordinates from the element location or from a lookup you own.

The page can sit in an iframe on an IDMP dashboard. The iframe URL is this service, for example `http://127.0.0.1:8095/`.

## What the page receives

```json
{
  "source": "TDengine",
  "assets": [
    {"id": "PUMP-12", "lon": -90.1994, "lat": 38.627, "height": 12, "reading": 42.5, "status": "OK", "ts": "2026-10-15T21:00:00.000Z"}
  ]
}
```

`id` is the Cesium entity id. The same id on the next poll updates that point in place.

## Troubleshooting

| What you see | What it usually is |
|---|---|
| The bar says it cannot reach taosAdapter | `TAOS_URL` host is wrong. Inside Docker, `localhost` is the container. |
| `/api/assets` is `{"assets":[]}` | Latitude or longitude is null. Those rows are dropped. |
| The globe is blank | Open `http://127.0.0.1:8095/`, not the HTML file directly. The imagery in this package does not need a Cesium ion token. |
| A new insert never shows | The service caches for 4 seconds and the page polls every 5 seconds. |
| TDengine load grows with every viewer | Browsers are querying the database themselves. Keep the cache in `server.py`. |
