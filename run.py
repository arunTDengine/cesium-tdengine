#!/usr/bin/env python3
"""Load a scenario, start the globe, and open it.

    python3 run.py
    python3 run.py fleet
"""

from __future__ import annotations

import sys
import webbrowser

import server


def scenario_names() -> list[str]:
    root = server.ROOT / "scenarios"
    if not root.is_dir():
        return []
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "query.sql").is_file()
    )


def load(name: str) -> None:
    folder = server.ROOT / "scenarios" / name
    query_path = folder / "query.sql"
    if not query_path.is_file():
        known = ", ".join(scenario_names()) or "(none)"
        raise SystemExit(f"No scenario '{name}'. Available scenarios: {known}")
    server.QUERY_FILE = query_path
    seed_path = folder / "seed.sql"
    if seed_path.is_file():
        for statement in server.statements(seed_path):
            server.query(statement)
    print(f"Scenario  {name}", flush=True)


def main() -> None:
    server.load_env()
    name = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if name in ("-h", "--help"):
        print("Usage: python3 run.py [scenario]")
        print("Scenarios: " + ", ".join(scenario_names()))
        return
    load(name)
    url = server.start()
    print(f"Open      {url}", flush=True)
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
