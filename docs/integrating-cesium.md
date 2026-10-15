# Connecting CesiumJS

CesiumJS draws a globe. TDengine stores the time series for the assets on that globe. This package is the connection between them. The service queries taosAdapter and returns JSON. The page creates one Cesium entity per asset and refreshes it in place.

The package is published at [github.com/arunTDengine/cesium-tdengine](https://github.com/arunTDengine/cesium-tdengine).

A wind farm, a fleet, a pipeline, or a set of fixed instruments uses the same service. Change the query to match the schema you already have.

`scenarios/sample` and `scenarios/fleet` are examples. Copy one of those directories, point `seed.sql` and `query.sql` at your own tables, and pass the new directory name when you start the service. The page, the service, and the JSON fields stay the same, so that copy is the start of your own Cesium scene.

Credentials remain on the service. The browser receives coordinates and measurements only.

## Requirements

Prepare the following:

1. TDengine 3.x is installed and running. See [Get Started](https://docs.tdengine.com/get-started/).
2. taosAdapter is running, and the machine that hosts this service can reach it. The REST interface is `http://<host>:6041/rest/sql` on a standard installation. Use the host and port where taosAdapter listens in your environment.
3. A TDengine user and password. The installation defaults are `root` and `taosdata`.
4. Python 3.9 or later. The service uses the standard library.
5. A browser that can load CesiumJS 1.114 from the Cesium CDN. The included page supplies its own imagery, so a Cesium ion token is optional.

## Configure the service

The service reads its connection from the process environment.

| Variable | Default | Purpose |
|---|---|---|
| `TAOS_URL` | `http://localhost:6041/rest/sql` | taosAdapter REST address. |
| `TAOS_USER` | `root` | TDengine user. |
| `TAOS_PASSWORD` | `taosdata` | TDengine password. |
| `HOST` | `127.0.0.1` | Bind address for the page. |
| `PORT` | `8095` | Bind port for the page. |

`.env.example` records the same names. Export the variables before starting the process. The SQL text is sent as the raw request body with HTTP Basic authentication. taosAdapter returns column names in `column_meta`. Alias expressions in the query so the names match the fields below.

## Start a scenario

From the package directory, run `run.py` with Python. That command loads a scenario, starts the service, and opens the page. With no argument the scenario is `scenarios/sample`, which creates database `cesium_sample` and three fixed assets. A second argument is the name of another directory under `scenarios/`. `scenarios/fleet` is a moving-asset scenario. A scenario directory contains `seed.sql`, which creates the tables and writes the current values, and `query.sql`, which the page reads.

Set `TAOS_URL` to the taosAdapter address for your installation before running the command. When that variable is unset, a `.env` file in the package directory supplies it. The standard address is `http://localhost:6041/rest/sql`. If the bind port is already taken, the service uses the next free port and prints the address it opened.

`server.py` serves whatever `query.sql` is in the package root and does not load a scenario. Opening the HTML file directly leaves the globe without data, because the page requests `/api/assets` from the service.

## What the page requires

`GET /api/assets` returns an object with `source` and `assets`. Each asset uses these fields.

| Field | Required | Meaning |
|---|---|---|
| `id` | Yes | Stable asset identifier. The page uses it as the Cesium entity id, so later refreshes update the same object. |
| `lon` | Yes | Longitude, decimal degrees. Cesium takes longitude first. |
| `lat` | Yes | Latitude, decimal degrees. |
| `height` | No | Meters above the ellipsoid. A missing value is drawn at 0. |
| Any other column | No | Shown when the asset is selected. `status` colors the point for `OK`, `WARN`, and `ALARM`. |

Rows with a null longitude or latitude are omitted. The service caches the JSON response for a few seconds so each open browser does not query TDengine on its own timer. The page refreshes about every five seconds.

## Map your tables

Edit `query.sql`. Keep the aliases `id`, `lon`, `lat`, and `height`.

| Scene | Store longitude and latitude | Query |
|---|---|---|
| Site, turbine, building, well, or meter | Tags on the supertable. The coordinate is not a new sample on every insert. | Latest measurements with `LAST`, grouped by child table. One child table is one entity. |
| Vehicle, aircraft, vessel, or person | Columns beside the timestamp. The coordinate is the time series. | Latest longitude and latitude for the current position. |

`examples/fixed-assets.sql` and `examples/moving-fleet.sql` are those two forms. Copy the relevant file over `query.sql` and rename the database, table, and columns.

Group by `tbname` when each child table is one asset. Alias every `LAST` expression. Without an alias, `LAST(longitude)` is returned as `last(longitude)`, and the page does not treat that key as a coordinate.

## Tracks

The asset feed is the current position. A path is a second query, downsampled so a long history stays small.

Copy `examples/track.sql` to `track.sql` in the package directory. Set the table, the time window, and the interval for your data. The token `{id}` is replaced with the asset id from `GET /api/track`. The included page draws the current position. A page that draws the path reads that second feed and builds a sampled position from `ts`, `lon`, `lat`, and `height`.

## TDengine IDMP

When the assets are already elements in TDengine IDMP, keep the page and read attribute values in the service. IDMP attributes are bound to TDengine columns, so the measurements still come from TDengine. The service then holds an IDMP token instead of a SQL statement.

1. Authenticate with `POST /api/v1/users/login` and send that token on later calls.
2. List the child elements that belong on the globe.
3. Cache the attribute identifiers for each element. They change rarely.
4. Read the current values and return the same asset fields: `id`, `lon`, `lat`, `height`, and the measurements to display.

Take coordinates from the element location, or from a lookup the service owns. Cache the assembled JSON for a few seconds, as the SQL path does.

The page can be placed in an IDMP dashboard as an iframe. The iframe address is the service address. See [Embedding Panels and Dashboards](https://idmpdocs.tdengine.com/integrating-with-other-systems/).

## Troubleshooting

| What you see | What to check |
|---|---|
| The page cannot reach taosAdapter | `TAOS_URL` is the host and port where taosAdapter is listening, and `TAOS_USER` and `TAOS_PASSWORD` match that installation. |
| The asset list is empty | The query returns rows, and longitude and latitude are present. Null coordinates are dropped. |
| The globe has no imagery or no points | The address opened in the browser is the one printed by the service. |
| A point is far from the asset | `lon` and `lat` are in the correct order. Cesium expects longitude first. |
| Points duplicate or jump | `id` is stable across refreshes. Use the asset identifier, not the timestamp. |
| A new value is slow to appear | The service cache is a few seconds, then the page refreshes. |
| TDengine load grows with every viewer | Queries stay in this service. The cache is what keeps one result shared. |
