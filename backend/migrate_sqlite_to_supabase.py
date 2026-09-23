from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database.db import engine as postgres_engine
from app.models.models import (
    User,
    AutomationSettings,
    Job,
    Application,
    Email,
    ActivityEvent,
    IntegratorStatus,
    EmailAccount,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = PROJECT_ROOT / "autoai.db"

SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

sqlite_engine = create_engine(SQLITE_URL)

SQLiteSession = sessionmaker(
    bind=sqlite_engine,
    autocommit=False,
    autoflush=False,
)

PostgresSession = sessionmaker(
    bind=postgres_engine,
    autocommit=False,
    autoflush=False,
)


MODELS = [
    User,
    AutomationSettings,
    Job,
    Application,
    Email,
    ActivityEvent,
    IntegratorStatus,
    EmailAccount,
]


def migrate_table(sqlite_session, postgres_session, model):
    table_name = model.__tablename__

    rows = sqlite_session.query(model).all()

    print(f"{table_name}: {len(rows)} rows")

    if not rows:
        return 0

    postgres_session.query(model).delete()

    for row in rows:
        data = {
            column.name: getattr(row, column.name)
            for column in model.__table__.columns
        }

        postgres_session.add(model(**data))

    return len(rows)


def reset_sequences():
    print()
    print("Resetting PostgreSQL sequences...")

    with postgres_engine.begin() as conn:
        for model in MODELS:
            table = model.__tablename__

            result = conn.execute(
                text(
                    f"""
                    SELECT pg_get_serial_sequence(
                        'public.{table}',
                        'id'
                    )
                    """
                )
            )

            sequence = result.scalar()

            if not sequence:
                continue

            result = conn.execute(
                text(
                    f"""
                    SELECT COALESCE(MAX(id), 0)
                    FROM public.{table}
                    """
                )
            )

            max_id = result.scalar()

            if max_id > 0:
                conn.execute(
                    text(
                        "SELECT setval("
                        ":sequence_name, "
                        ":max_id, "
                        "true)"
                    ),
                    {
                        "sequence_name": sequence,
                        "max_id": max_id,
                    },
                )

                print(
                    f"{table}: sequence → {max_id}"
                )


def main():
    if not SQLITE_PATH.exists():
        raise SystemExit(
            f"SQLite database not found: {SQLITE_PATH}"
        )

    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    total = 0

    try:
        print("=== SQLite → Supabase Migration ===")
        print()
        print(f"SQLite source: {SQLITE_PATH}")
        print()

        for model in MODELS:
            total += migrate_table(
                sqlite_session,
                postgres_session,
                model,
            )

        postgres_session.commit()

        reset_sequences()

        print()
        print(
            f"Migration completed successfully. "
            f"{total} rows migrated."
        )

    except Exception:
        postgres_session.rollback()
        raise

    finally:
        sqlite_session.close()
        postgres_session.close()


if __name__ == "__main__":
    main()
