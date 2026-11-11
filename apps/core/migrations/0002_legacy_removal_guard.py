"""Require explicit consent before deleting nonempty retired-feature data."""
import os
from django.db import migrations

TABLES = (
    'explore_itinerary_stops', 'explore_itineraries', 'explore_visit_checkins',
    'dashboard_itinerary_places', 'dashboard_user_itineraries',
    'dashboard_saved_places', 'dashboard_search_history', 'dashboard_user_hobbies',
    'dashboard_user_reviews',
)


def guard(apps, schema_editor):
    connection = schema_editor.connection
    existing = set(connection.introspection.table_names())
    populated = []
    with connection.cursor() as cursor:
        for table in TABLES:
            if table in existing:
                cursor.execute('SELECT 1 FROM %s LIMIT 1' % schema_editor.quote_name(table))
                if cursor.fetchone():
                    populated.append(table)
    if populated and os.environ.get('EK_APPROVE_LEGACY_REMOVAL') != '1':
        raise RuntimeError(
            'Retired-feature tables contain data: ' + ', '.join(populated) +
            '. Back up and verify the database, then set EK_APPROVE_LEGACY_REMOVAL=1 '
            'only after approval. No retired-feature tables were removed by this guard.'
        )


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial'), ('itineraries', '0002_initial'), ('visits', '0001_initial')]
    operations = [migrations.RunPython(guard, migrations.RunPython.noop)]
