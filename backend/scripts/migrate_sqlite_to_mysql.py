"""Migrate the legacy SQLite database into the configured MySQL database.

Run from the ``backend`` directory:

    python scripts/migrate_sqlite_to_mysql.py

The script is idempotent: every row is written with ``ON DUPLICATE KEY UPDATE``
keyed on the primary key, so re-running it safely refreshes existing rows
instead of creating duplicates. Primary keys are preserved, which keeps
``appointment.patient_id`` / ``appointment.doctor_id`` references valid.
"""

import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine  # noqa: E402

SQLITE_PATH = BACKEND_DIR / "healthcare.db"

# (sqlite table, columns, {column: fallback for junk values}). Order matters
# only for readability, the models declare plain int columns rather than
# real FKs. `age` is NOT NULL so junk becomes 0; nullable FKs become NULL.
TABLES = [
    ("user", ["id", "email", "password_hash", "role"], {"id": 0}),
    (
        "patient",
        ["id", "user_id", "name", "age", "gender"],
        {"id": 0, "user_id": None, "age": 0},
    ),
    (
        "doctor",
        ["id", "user_id", "name", "specialization"],
        {"id": 0, "user_id": None},
    ),
    ("department", ["id", "name"], {"id": 0}),
    (
        "appointment",
        [
            "id",
            "patient_id",
            "doctor_id",
            "appointment_date",
            "appointment_time",
        ],
        {"id": 0, "patient_id": 0, "doctor_id": 0},
    ),
]

FIXED = []


def coerce_int(value, fallback, table, row_id, column):
    """SQLite columns are dynamically typed, so an INTEGER column can hold
    text like 'hello'. MySQL strict mode rejects that, so junk values are
    coerced to a safe fallback and reported instead of dropping the row."""
    if value is None or isinstance(value, int) and not isinstance(value, bool):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        FIXED.append(
            "%s id=%s %s: %r -> %r" % (table, row_id, column, value, fallback)
        )
        return fallback


def sqlite_rows(conn, table, columns):
    """Yield rows from SQLite as dicts, tolerating missing optional columns."""
    existing = {
        r[1]
        for r in conn.execute("PRAGMA table_info(%s)" % table).fetchall()
    }
    missing = [c for c in columns if c not in existing]
    if missing:
        print("  ! %s: SQLite is missing %s, filling NULL" % (table, missing))

    select_cols = ", ".join(
        c if c in existing else "NULL AS %s" % c for c in columns
    )
    cursor = conn.execute("SELECT %s FROM %s" % (select_cols, table))
    names = [d[0] for d in cursor.description]
    for row in cursor.fetchall():
        yield dict(zip(names, row))


def report_orphans(conn):
    """SQLite had no FK enforcement, so some appointments may point at rows
    that were deleted. MySQL also has no FK constraints here, so these copy
    across as-is; we just tell the user what to clean up."""
    checks = [
        ("appointment -> patient", "select count(*) from appointment a "
         "where a.patient_id not in (select id from patient)"),
        ("appointment -> doctor", "select count(*) from appointment a "
         "where a.doctor_id not in (select id from doctor)"),
    ]
    for label, sql in checks:
        n = conn.execute(sql).fetchone()[0]
        if n:
            print("  ! %d orphaned rows: %s" % (n, label))


def main():
    if not SQLITE_PATH.exists():
        print("SQLite source not found: %s" % SQLITE_PATH)
        return 1

    print("Source (SQLite): %s" % SQLITE_PATH)
    print("Target (MySQL) : %s" % engine.url.render_as_string(hide_password=True))
    print()

    src = sqlite3.connect(SQLITE_PATH)
    src.row_factory = sqlite3.Row

    # MySQL needs the tables to exist before we can copy into them.
    from app.database.database import create_db_and_tables

    create_db_and_tables()

    total = 0
    with engine.begin() as dest:
        for table, columns, int_cols in TABLES:
            rows = list(sqlite_rows(src, table, columns))
            if not rows:
                print("%-12s 0 rows (skipped)" % table)
                continue

            # Sanitise dynamically typed SQLite values before they reach MySQL.
            for row in rows:
                for col, fallback in int_cols.items():
                    row[col] = coerce_int(
                        row.get(col), fallback, table, row.get("id"), col
                    )

            placeholders = ", ".join(["%s"] * len(columns))
            collist = ", ".join("`%s`" % c for c in columns)
            # Update every non-PK column on conflict so re-runs are safe.
            updates = ", ".join(
                "`%s` = VALUES(`%s`)" % (c, c) for c in columns if c != "id"
            )
            sql = "INSERT INTO `%s` (%s) VALUES (%s)" % (
                table,
                collist,
                placeholders,
            )
            if updates:
                sql += " ON DUPLICATE KEY UPDATE " + updates

            params = [tuple(r[c] for c in columns) for r in rows]
            dest.exec_driver_sql(sql, params)

            total += len(rows)
            print("%-12s %d rows migrated" % (table, len(rows)))

    src.close()
    print("-" * 40)
    print("Total rows migrated: %d" % total)

    if FIXED:
        print("\nData cleaned during migration:")
        for line in FIXED:
            print("  * %s" % line)

    print("\nData quality notes (also present in the SQLite source):")
    report_orphans(sqlite3.connect(SQLITE_PATH))

    print("\nVerification:")
    ok = True
    with engine.connect() as check:
        for table, _columns, _int_cols in TABLES:
            expected = sqlite3.connect(SQLITE_PATH).execute(
                'select count(*) from "%s"' % table
            ).fetchone()[0]
            actual = check.exec_driver_sql(
                'select count(*) from `%s`' % table
            ).scalar()
            flag = "OK" if expected == actual else "MISMATCH"
            if expected != actual:
                ok = False
            print("  %-12s sqlite=%-4d mysql=%-4d %s"
                  % (table, expected, actual, flag))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())