"""Drop approved unmanaged legacy dashboard tables, child tables first."""
from django.db import migrations
from importlib import import_module


def recheck(apps, schema_editor):
    import_module("apps.core.migrations.0002_legacy_removal_guard").guard(apps, schema_editor)

TABLES = (
    'dashboard_itinerary_places', 'dashboard_user_itineraries',
    'dashboard_saved_places', 'dashboard_search_history',
    'dashboard_user_hobbies', 'dashboard_user_reviews',
)


def drop_legacy(apps, schema_editor):
    existing = set(schema_editor.connection.introspection.table_names())
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            if table in existing:
                cursor.execute('DROP TABLE ' + schema_editor.quote_name(table))


class Migration(migrations.Migration):
    dependencies = [('core', '0002_legacy_removal_guard'), ('itineraries', '0003_remove_itineraries'), ('visits', '0002_remove_visits')]
    operations = [migrations.RunPython(recheck, migrations.RunPython.noop), migrations.RunPython(drop_legacy)]
