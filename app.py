from flask import Flask, render_template
from pathlib import Path
import csv
import json
import os

app = Flask(__name__, template_folder="templates", static_folder="static")


def load_demo_route():
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
                            [41.8979, 12.4082]
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
                            {"id": "S10", "name": "Trastevere", "lat": 41.8979, "lon": 12.4082, "sequence": 10}
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
                            {"from": "Trastevere Sud", "to": "Trastevere", "turn": "svolta a sinistra"}
                        ]
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
                            [41.8944, 12.4733]
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
                            {"id": "S1", "name": "Piazza Venezia", "lat": 41.8944, "lon": 12.4733, "sequence": 10}
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
                            {"from": "Via del Corso", "to": "Piazza Venezia", "turn": "svolta a destra"}
                        ]
                    }
                ]
            }
        ]
    }


def load_gtfs_route():
    """Load GTFS data from a local data/gtfs folder if provided.

    The app is ready for real GTFS imports, but does not claim to have real
    official Rome data unless the files are placed in the expected folder.
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
        with open(gtfs_dir / "routes.txt", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                routes[row["route_id"]] = row

        trips = {}
        with open(gtfs_dir / "trips.txt", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                trips[row["trip_id"]] = row

        stops = {}
        with open(gtfs_dir / "stops.txt", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                stops[row["stop_id"]] = {
                    "id": row["stop_id"],
                    "name": row.get("stop_name", row["stop_id"]),
                    "lat": float(row["stop_lat"]),
                    "lon": float(row["stop_lon"]),
                }

        stop_times = {}
        with open(gtfs_dir / "stop_times.txt", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_times.setdefault(row["trip_id"], []).append({
                    "stop_id": row["stop_id"],
                    "arrival": row.get("arrival_time", "00:00:00"),
                    "departure": row.get("departure_time", "00:00:00"),
                    "sequence": int(row.get("stop_sequence", 0)),
                })

        line_id = next(iter(routes.keys()), None)
        if not line_id:
            return None

        route_data = {
            "mode": "gtfs",
            "notice": "Dati GTFS caricati. La navigazione reale richiede GTFS completo e coordinate stradali accurate.",
            "lines": [{
                "id": line_id,
                "name": f"Linea {route_data_name(routes[line_id]) or line_id}",
                "variants": [{
                    "id": "gtfs-primary",
                    "direction": routes[line_id].get("route_short_name", line_id),
                    "path": [],
                    "stops": []
                }]
            }]
        }

        gtfs_stops = []
        for trip_id, stop_list in stop_times.items():
            ordered = sorted(stop_list, key=lambda s: int(s["sequence"]))
            gtfs_stops.extend([stops[item["stop_id"]] for item in ordered if item["stop_id"] in stops])
            if gtfs_stops:
                break

        route_data["lines"][0]["variants"][0]["stops"] = gtfs_stops[:20]
        if gtfs_stops:
            route_data["lines"][0]["variants"][0]["path"] = [
                [stop["lat"], stop["lon"]] for stop in gtfs_stops[:20]
            ]

        return route_data
    except (KeyError, ValueError, OSError):
        return None


def route_data_name(route):
    return route.get("route_short_name") or route.get("route_long_name") or "GTFS"


@app.route("/")
def index():
    route = load_gtfs_route() or load_demo_route()
    return render_template("index.html", route_json=route)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
