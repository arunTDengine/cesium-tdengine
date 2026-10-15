# CesiumJS and TDengine

This package places TDengine assets on a CesiumJS globe. A small service reads taosAdapter and serves one JSON object per asset. The page draws one entity per object. Database credentials stay with the service.

The package is published at [github.com/arunTDengine/cesium-tdengine](https://github.com/arunTDengine/cesium-tdengine).

Use it for a fixed site, a moving fleet, or assets that already exist as elements in TDengine IDMP. The page stays the same. The query changes.

The scenarios in this package are examples. Copy a directory under `scenarios/`, point it at your own tables, and run that name to build your own Cesium scene on the same service.

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

## Start a scenario

`run.py` is the one command. It loads a scenario into TDengine, starts the service, and opens the page. With no argument it loads `scenarios/sample`: three fixed assets in database `cesium_sample`. `python3 run.py fleet` loads the moving-asset scenario instead. Each directory under `scenarios/` is a scenario, with `seed.sql` and `query.sql`.

Set `TAOS_URL` when taosAdapter is not at `http://localhost:6041/rest/sql`. A file named `.env` in this directory is applied for any variable that is not already set. If the chosen port is in use, the service takes the next free port and prints that address.

`server.py` starts the page against the current `query.sql` and does not load a scenario.

## Your tables

Edit `query.sql` so each row provides `id`, `lon`, `lat`, and optionally `height`. Other columns appear when an operator selects an asset. `examples/fixed-assets.sql` is the form for assets that do not move. `examples/moving-fleet.sql` is the form for assets that do. Remove the sample marker in `query.sql` before using your own statement.

For a path over time, copy `examples/track.sql` to `track.sql` beside `server.py` and name your table and columns there.
