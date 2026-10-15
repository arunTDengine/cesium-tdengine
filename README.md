# CesiumJS and TDengine

This package places TDengine assets on a CesiumJS globe. A small service reads taosAdapter and serves one JSON object per asset. The page draws one entity per object. Database credentials stay with the service.

Use it for a fixed site, a moving fleet, or assets that already exist as elements in TDengine IDMP. The page stays the same. The query changes.

The full guide is in [docs/integrating-cesium.md](docs/integrating-cesium.md).

## Requirements

- TDengine 3.x with taosAdapter
- Python 3.9 or later, standard library only
- A browser that can load CesiumJS from the Cesium CDN

## Connection

Set these variables in the environment of the service. The defaults match taosAdapter on the same machine, using the standard REST port and the default TDengine user.

| Variable | Default | Purpose |
|---|---|---|
| `TAOS_URL` | `http://localhost:6041/rest/sql` | taosAdapter REST address. Use the host and port where taosAdapter is listening. |
| `TAOS_USER` | `root` | TDengine user. |
| `TAOS_PASSWORD` | `taosdata` | TDengine password. |
| `HOST` | `127.0.0.1` | Address the page binds to. |
| `PORT` | `8095` | Port the page binds to. |

`.env.example` lists the same names. The service reads the process environment.

## Start

From this directory, start `server.py` with Python 3.9 or later. The process prints the page address. Open that address in a browser.

On the first request, if `query.sql` is still the included sample and `geo.assets` does not exist, the service creates database `geo` and three sample assets.

## Your tables

Edit `query.sql` so each row provides `id`, `lon`, `lat`, and optionally `height`. Other columns appear when an operator selects an asset. `examples/fixed-assets.sql` is the form for assets that do not move. `examples/moving-fleet.sql` is the form for assets that do. Remove the sample marker in `query.sql` before using your own statement.

For a path over time, copy `examples/track.sql` to `track.sql` beside `server.py` and name your table and columns there.
