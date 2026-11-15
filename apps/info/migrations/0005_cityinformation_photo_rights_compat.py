"""Map photo-rights columns, preserving pre-existing local database values.

Some installations already contain these columns. Add only missing columns;
never drop a column on reverse. This migration is not run by the PC updater.
"""
import re

from django.db import migrations, models


FIELDS = (
    ("photo_license", lambda: models.CharField(blank=True, max_length=100)),
    ("photo_license_url", lambda: models.URLField(blank=True, max_length=1000)),
    ("photo_source_url", lambda: models.URLField(blank=True, max_length=1000)),
)


def add_missing_columns(apps, schema_editor):
    CityInformation = apps.get_model("info", "CityInformation")
    table = CityInformation._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name: column
            for column in schema_editor.connection.introspection.get_table_description(cursor, table)
        }
        sqlite_types = {}
        if schema_editor.connection.vendor == "sqlite":
            cursor.execute(f"PRAGMA table_info({schema_editor.quote_name(table)})")
            sqlite_types = {row[1]: row[2] for row in cursor.fetchall()}
    # Check every existing column before making any schema change. Retain all
    # existing values; incompatible layouts require manual review instead.
    for name, factory in FIELDS:
        if name not in columns:
            continue
        column = columns[name]
        kind = schema_editor.connection.introspection.get_field_type(column.type_code, column)
        expected = factory().max_length
        size = column.internal_size
        if kind == "CharField" and size is None and name in sqlite_types:
            match = re.fullmatch(r"(?i)varchar\s*\(\s*(\d+)\s*\)", sqlite_types[name])
            size = int(match.group(1)) if match else None
        if kind not in ("CharField", "TextField") or column.null_ok or (
            kind == "CharField" and (size is None or size < expected)
        ):
            raise RuntimeError(f"Existing {table}.{name} has an incompatible definition; no fields added.")
    expected_columns = {field.column for field in CityInformation._meta.local_fields} | {name for name, _ in FIELDS}
    if any(name not in columns for name, _ in FIELDS) and set(columns) - expected_columns:
        raise RuntimeError(f"Unexpected extra columns on {table}; manual review required before adding fields.")
    # Register already-existing compatible columns on the historical model so
    # SQLite table rebuilds cannot discard them when another column is missing.
    for name, factory in FIELDS:
        if name in columns:
            factory().contribute_to_class(CityInformation, name)
    for name, factory in FIELDS:
        if name in columns:
            continue
        field = factory()
        field.set_attributes_from_name(name)
        field.model = CityInformation
        schema_editor.add_field(CityInformation, field)
        # SQLite may rebuild the table on each addition; its next rebuild must
        # include fields added in the preceding iteration.
        field.contribute_to_class(CityInformation, name)


class Migration(migrations.Migration):
    dependencies = [("info", "0004_cityinformation_photo_credit")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(add_missing_columns, migrations.RunPython.noop)],
            state_operations=[
                migrations.AddField(
                    model_name="cityinformation", name="photo_license",
                    field=models.CharField(blank=True, max_length=100),
                ),
                migrations.AddField(
                    model_name="cityinformation", name="photo_license_url",
                    field=models.URLField(blank=True, max_length=1000),
                ),
                migrations.AddField(
                    model_name="cityinformation", name="photo_source_url",
                    field=models.URLField(blank=True, max_length=1000),
                ),
            ],
        ),
    ]
