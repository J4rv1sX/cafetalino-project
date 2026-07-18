"""Load active vending-machine readings into SQLite.

Readings are grouped by physical location (lat/lng), not machine_id,
since units churn independently of where they're actually placed.
Reuses the validated CSV-loading/grouping logic from _shared.py.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from _shared import CSV_PATH, build_canonical_locations, filter_active, load_data

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "data" / "cafetalino.db"

SCHEMA_SQL = """
DROP TABLE IF EXISTS readings;
DROP TABLE IF EXISTS locations;

CREATE TABLE locations (
    id             INTEGER PRIMARY KEY,
    name           TEXT NOT NULL,
    lat            REAL NOT NULL,
    lng            REAL NOT NULL,
    water_capacity REAL NOT NULL,
    mix_capacity   REAL NOT NULL,
    UNIQUE (lat, lng)
);

CREATE TABLE readings (
    id                          INTEGER PRIMARY KEY,
    location_id                 INTEGER NOT NULL REFERENCES locations(id),
    date                        TEXT NOT NULL,
    raw_location_name           TEXT NOT NULL,
    cups                        INTEGER NOT NULL,
    water_remaining_pct         REAL,
    previous_refill_date        TEXT,
    days_since_previous_refill  INTEGER,
    bottled_water_ml            REAL NOT NULL,
    cup_units                   REAL NOT NULL,
    coffee_mix_g                REAL NOT NULL,
    chocolate_mix_g             REAL NOT NULL,
    cappuccino_mix_g            REAL NOT NULL,
    notes                       TEXT
);

CREATE INDEX idx_readings_location_date ON readings (location_id, date);
"""

WATER_CAPACITY_L = 20
MIX_CAPACITY_G = 1600
REDUCED_MIX_CAPACITY_G = 900
REDUCED_MIX_CAPACITY_LOCATIONS = {
    "Colegio Simón Rodríguez",
    "Paseo La Plata Junin",
}

READING_COLUMNS = [
    "location_id",
    "date",
    "raw_location_name",
    "cups",
    "water_remaining_pct",
    "previous_refill_date",
    "days_since_previous_refill",
    "bottled_water_ml",
    "cup_units",
    "coffee_mix_g",
    "chocolate_mix_g",
    "cappuccino_mix_g",
    "notes",
]


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)


def prepare_locations(roster: pd.DataFrame) -> pd.DataFrame:
    locations = roster[["name", "lat", "lng"]].copy()
    locations["water_capacity"] = WATER_CAPACITY_L
    locations["mix_capacity"] = locations["name"].apply(
        lambda name: REDUCED_MIX_CAPACITY_G if name in REDUCED_MIX_CAPACITY_LOCATIONS else MIX_CAPACITY_G
    )
    return locations


def prepare_readings(active: pd.DataFrame, location_map: pd.DataFrame) -> pd.DataFrame:
    df = active.merge(location_map, on=["lat", "lng"], how="left", validate="many_to_one")
    assert df["location_id"].notna().all(), "every active reading must resolve to a location"

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df["previous_refill_date"] = df["previous_refill_date"].dt.strftime("%Y-%m-%d")
    df["days_since_previous_refill"] = df["days_since_previous_refill"].astype("Int64")

    return df[READING_COLUMNS]


def main() -> None:
    df = load_data(CSV_PATH)
    active = filter_active(df)
    roster = build_canonical_locations(active)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)

        prepare_locations(roster).to_sql("locations", conn, if_exists="append", index=False)
        location_map = pd.read_sql("SELECT id AS location_id, lat, lng FROM locations", conn)
        prepare_readings(active, location_map).to_sql("readings", conn, if_exists="append", index=False)
        conn.commit()

        n_locations = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
        n_readings = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]

        print("\n=== Done ===")
        print(f"locations: {n_locations} rows")
        print(f"readings:  {n_readings} rows")
        print(f"db file: {DB_PATH}")

        print("\nspot check -- top 3 locations by reading count:")
        rows = conn.execute(
            "SELECT l.name, COUNT(*) AS n FROM readings r "
            "JOIN locations l ON l.id = r.location_id "
            "GROUP BY l.id ORDER BY n DESC LIMIT 3"
        ).fetchall()
        for name, n in rows:
            print(f"  {name}: {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
