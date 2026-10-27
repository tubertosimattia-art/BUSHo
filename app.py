from __future__ import annotations

import csv
import os
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math

    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_route_name(route: dict) -> str:
    return route.get("route_short_name") or route.get("route_long_name") or "GTFS"


def load_demo_route() -> dict:
    return {
        "mode": "demo",
        "notice": "MODALITÀ DEMO: nessun GTFS ufficiale caricato. I dati sono un prototipo locale per test UI e logica di navigazione.",
        "lines": [
            {
                "id": "90",
                "name": "Linea 90",
                "variants": [
                    {
                        "id": "inbound",
                        "direction": "Piazza Venezia → Trastevere",
                        "path": [
                            [41.8944, 12.4733],
                            [41.8950, 12.4720],
                            [41.8958, 12.4708],
                            [41.8969, 12.4699],
                            [41.8980, 12.4689],
                            [41.8996, 12.4674],
                            [41.9018, 12.4660],
                            [41.9039, 12.4646],
                            [41.9056, 12.4628],
                            [41.9071, 12.4608],
                            [41.9089, 12.4578],
                            [41.9102, 12.4548],
                            [41.9114, 12.4511],
                            [41.9124, 12.4478],
                            [41.9130, 12.4439],
                            [41.9127, 12.4395],
                            [41.9118, 12.4354],
                            [41.9103, 12.4317],
                            [41.9088, 12.4286],
                            [41.9075, 12.4254],
                            [41.9061, 12.4228],
                            [41.9048, 12.4204],
                            [41.9036, 12.4179],
                            [41.9023, 12.4156],
                            [41.9008, 12.4132],
                            [41.8993, 12.4107],
                            [41.8979, 12.4082],
                        ],
                        "stops": [
                            {"id": "S1", "name": "Piazza Venezia", "lat": 41.8944, "lon": 12.4733, "sequence": 1},
                            {"id": "S2", "name": "Via del Corso", "lat": 41.8969, "lon": 12.4699, "sequence": 2},
                            {"id": "S3", "name": "Piazza Colonna", "lat": 41.8996, "lon": 12.4674, "sequence": 3},
                            {"id": "S4", "name": "Via del Babuino", "lat": 41.9039, "lon": 12.4646, "sequence": 4},
                            {"id": "S5", "name": "Piazza del Popolo", "lat": 41.9089, "lon": 12.4578, "sequence": 5},
                            {"id": "S6", "name": "Via Flaminia", "lat": 41.9124, "lon": 12.4478, "sequence": 6},
                            {"id": "S7", "name": "Ponte Milvio", "lat": 41.9130, "lon": 12.4439, "sequence": 7},
                            {"id": "S8", "name": "Tiburtina", "lat": 41.9103, "lon": 12.4317, "sequence": 8},
                            {"id": "S9", "name": "Trastevere Sud", "lat": 41.9023, "lon": 12.4156, "sequence": 9},
                            {"id": "S10", "name": "Trastevere", "lat": 41.8979, "lon": 12.4082, "sequence": 10},
                        ],
                        "instructions": [
                            {"from": "Piazza Venezia", "to": "Via del Corso", "turn": "prosegui dritto"},
                            {"from": "Via del Corso", "to": "Piazza Colonna", "turn": "tenere la destra"},
                            {"from": "Piazza Colonna", "to": "Via del Babuino", "turn": "prosegui dritto"},
                            {"from": "Via del Babuino", "to": "Piazza del Popolo", "turn": "svolta a destra"},
                            {"from": "Piazza del Popolo", "to": "Via Flaminia", "turn": "prosegui dritto"},
                            {"from": "Via Flaminia", "to": "Ponte Milvio", "turn": "svolta a sinistra"},
                            {"from": "Ponte Milvio", "to": "Tiburtina", "turn": "tenere la destra"},
                            {"from": "Tiburtina", "to": "Trastevere Sud", "turn": "prosegui dritto"},
                            {"from": "Trastevere Sud", "to": "Trastevere", "turn": "svolta a sinistra"},
                        ],
                    },
                    {
                        "id": "outbound",
                        "direction": "Trastevere → Piazza Venezia",
                        "path": [
                            [41.8979, 12.4082],
                            [41.8992, 12.4101],
                            [41.9006, 12.4124],
                            [41.9023, 12.4156],
                            [41.9040, 12.4188],
                            [41.9059, 12.4222],
                            [41.9077, 12.4258],
                            [41.9095, 12.4301],
                            [41.9108, 12.4348],
                            [41.9117, 12.4396],
                            [41.9128, 12.4448],
                            [41.9123, 12.4501],
                            [41.9111, 12.4543],
                            [41.9099, 12.4583],
                            [41.9076, 12.4620],
                            [41.9052, 12.4646],
                            [41.9028, 12.4672],
                            [41.9005, 12.4688],
                            [41.8985, 12.4701],
                            [41.8967, 12.4718],
                            [41.8944, 12.4733],
                        ],
                        "stops": [
                            {"id": "S10", "name": "Trastevere", "lat": 41.8979, "lon": 12.4082, "sequence": 1},
                            {"id": "S9", "name": "Trastevere Sud", "lat": 41.9023, "lon": 12.4156, "sequence": 2},
                            {"id": "S8", "name": "Tiburtina", "lat": 41.9103, "lon": 12.4317, "sequence": 3},
                            {"id": "S7", "name": "Ponte Milvio", "lat": 41.9130, "lon": 12.4439, "sequence": 4},
                            {"id": "S6", "name": "Via Flaminia", "lat": 41.9124, "lon": 12.4478, "sequence": 5},
                            {"id": "S5", "name": "Piazza del Popolo", "lat": 41.9089, "lon": 12.4578, "sequence": 6},
                            {"id": "S4", "name": "Via del Babuino", "lat": 41.9039, "lon": 12.4646, "sequence": 7},
                            {"id": "S3", "name": "Piazza Colonna", "lat": 41.8996, "lon": 12.4674, "sequence": 8},
                            {"id": "S2", "name": "Via del Corso", "lat": 41.8969, "lon": 12.4699, "sequence": 9},
                            {"id": "S1", "name": "Piazza Venezia", "lat": 41.8944, "lon": 12.4733, "sequence": 10},
                        ],
                        "instructions": [
                            {"from": "Trastevere", "to": "Trastevere Sud", "turn": "prosegui dritto"},
                            {"from": "Trastevere Sud", "to": "Tiburtina", "turn": "svolta a destra"},
                            {"from": "Tiburtina", "to": "Ponte Milvio", "turn": "tenere la sinistra"},
                            {"from": "Ponte Milvio", "to": "Via Flaminia", "turn": "prosegui dritto"},
                            {"from": "Via Flaminia", "to": "Piazza del Popolo", "turn": "svolta a sinistra"},
                            {"from": "Piazza del Popolo", "to": "Via del Babuino", "turn": "prosegui dritto"},
                            {"from": "Via del Babuino", "to": "Piazza Colonna", "turn": "tenere la destra"},
                            {"from": "Piazza Colonna", "to": "Via del Corso", "turn": "prosegui dritto"},
                            {"from": "Via del Corso", "to": "Piazza Venezia", "turn": "svolta a destra"},
                        ],
                    },
                ],
            }
        ],
    }


def load_gtfs_route() -> dict | None:
    """Load GTFS data only if official files are placed in data/gtfs.

    This function does not invent missing values. If the folder is absent or
    incomplete, it returns None and the UI stays in demo mode.
    """
    base_dir = Path(__file__).resolve().parent
    gtfs_dir = base_dir / "data" / "gtfs"
    if not gtfs_dir.exists():
        return None

    required_files = ["routes.txt", "trips.txt", "stops.txt", "stop_times.txt"]
    if not all((gtfs_dir / name).exists() for name in required_files):
        return None

    try:
        routes = {}
        with open(gtfs_dir / "routes.txt", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                route_id = row.get("route_id")
                if route_id:
                    routes[route_id] = row

        if not routes:
            return None

        stops = {}
        with open(gtfs_dir / "stops.txt", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                stop_id = row.get("stop_id")
                if stop_id:
                    try:
                        stops[stop_id] = {
                            "id": stop_id,
                            "name": row.get("stop_name", stop_id),
                            "lat": float(row["stop_lat"]),
                            "lon": float(row["stop_lon"]),
                        }
                    except (KeyError, ValueError):
                        continue

        stop_times = {}
        with open(gtfs_dir / "stop_times.txt", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                trip_id = row.get("trip_id")
                stop_id = row.get("stop_id")
                if not trip_id or not stop_id:
                    continue
                stop_times.setdefault(trip_id, []).append({
                    "stop_id": stop_id,
                    "sequence": int(row.get("stop_sequence", 0) or 0),
                })

        route_variants = []
        for route_id, route in routes.items():
            selected_stops = []
            for trip_id, sequence in stop_times.items():
                ordered = sorted(sequence, key=lambda item: int(item["sequence"]))
                stop_ids = [item["stop_id"] for item in ordered if item["stop_id"] in stops]
                if stop_ids:
                    selected_stops = [stops[stop_id] for stop_id in stop_ids[:25]]
                    break
            if not selected_stops:
                continue

            route_variants.append({
                "id": f"{route_id}-primary",
                "direction": route.get("route_long_name") or route.get("route_short_name") or route_id,
                "path": [[stop["lat"], stop["lon"]] for stop in selected_stops],
                "stops": selected_stops,
                "instructions": [],
            })

        if not route_variants:
            return None

        return {
            "mode": "gtfs",
            "notice": "Dati GTFS caricati: la navigazione reale richiede una geometria stradale valida in shapes.txt e supporto GPS del browser.",
            "lines": [{
                "id": route_variants[0]["id"],
                "name": f"Linea {get_route_name(routes[next(iter(routes))])}",
                "variants": route_variants,
            }],
        }
    except (OSError, ValueError, csv.Error):
        return None


@app.route("/")
def index():
    route = load_gtfs_route() or load_demo_route()
    return render_template("index.html", route_json=route)


@app.route("/health")
def health():
    return {"status": "ok", "mode": "demo" if not load_gtfs_route() else "gtfs"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
