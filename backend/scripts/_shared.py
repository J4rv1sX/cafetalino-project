"""Shared CSV-loading/grouping logic for the consumption-data scripts.

Column names are translated to English immediately on load (see
COLUMN_RENAME) so everything downstream works with English identifiers.
Spanish only remains in data content (e.g. a location's `name` value),
never in column/table names.
"""

from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BACKEND_DIR / "data" / "consumo_insumos.csv"

COLUMN_RENAME = {
    "fecha": "date",
    "ubicacion": "raw_location_name",
    "latitud": "lat",
    "longitud": "lng",
    "estado": "status",
    "observaciones": "notes",
    "vasos": "cups",
    "agua_restante_pct": "water_remaining_pct",
    "fecha_recarga_anterior": "previous_refill_date",
    "dias_desde_recarga_anterior": "days_since_previous_refill",
    "agua_embotellada_ml": "bottled_water_ml",
    "vaso_pza": "cup_units",
    "mezcla_cafe_gr": "coffee_mix_g",
    "mezcla_chocolate_gr": "chocolate_mix_g",
    "mezcla_cappuccino_gr": "cappuccino_mix_g",
}


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["fecha", "fecha_recarga_anterior"])
    return df.rename(columns=COLUMN_RENAME)


def filter_active(df: pd.DataFrame) -> pd.DataFrame:
    active = df[df["status"] == "activo"].copy()
    print(f"\n=== Filtering to status == 'activo' ===\n{len(df)} rows -> {len(active)} rows")
    return active


def build_canonical_locations(active: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Canonical location roster (grouped by lat/lng) ===")

    def most_common(series: pd.Series) -> str:
        return series.value_counts().idxmax()

    grouped = active.groupby(["lat", "lng"])
    roster = grouped.agg(
        name=("raw_location_name", most_common),
        reading_count=("raw_location_name", "size"),
        raw_name_variant_count=("raw_location_name", "nunique"),
        raw_name_variants=("raw_location_name", lambda s: "; ".join(sorted(s.unique()))),
        machine_id_count=("machine_id", "nunique"),
        date_min=("date", "min"),
        date_max=("date", "max"),
        mean_water_remaining_pct=("water_remaining_pct", "mean"),
        mean_days_since_previous_refill=("days_since_previous_refill", "mean"),
        mean_cups=("cups", "mean"),
        mean_bottled_water_ml=("bottled_water_ml", "mean"),
        mean_cup_units=("cup_units", "mean"),
        mean_coffee_mix_g=("coffee_mix_g", "mean"),
        mean_chocolate_mix_g=("chocolate_mix_g", "mean"),
        mean_cappuccino_mix_g=("cappuccino_mix_g", "mean"),
    ).reset_index()

    roster = roster.sort_values("reading_count", ascending=False).reset_index(drop=True)

    print(f"{len(roster)} canonical locations found from {len(active)} active readings.")
    print(roster[["name", "lat", "lng", "reading_count", "raw_name_variant_count", "machine_id_count"]])

    merged = roster[roster["raw_name_variant_count"] > 1]
    if not merged.empty:
        print("\nLocations where multiple raw name spellings were merged by coordinate:")
        print(merged[["name", "reading_count", "raw_name_variants"]])

    return roster
