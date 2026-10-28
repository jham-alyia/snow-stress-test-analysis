from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB_PATH = PROCESSED / "calgary_snow.duckdb"

TABLES = {
    "weather": PROCESSED / "weather_clean.csv",
    "incidents": PROCESSED / "incidents_clean.csv",
}


def main():
    missing = [p for p in TABLES.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing cleaned files (run the clean step first):\n"
            + "\n".join(f"  {p}" for p in missing)
        )

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute("BEGIN")
        for name, path in TABLES.items():
            con.execute(
                f"CREATE OR REPLACE TABLE {name} AS "
                f"SELECT * FROM read_csv_auto('{path.as_posix()}')"
            )
        con.execute("COMMIT")

        for name in TABLES:
            n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            cols = con.execute(f"DESCRIBE {name}").fetchall()
            print(f"loaded {name}: {n:,} rows")
            for col_name, col_type, *_ in cols:
                print(f"    {col_name}: {col_type}")


if __name__ == "__main__":
    main()