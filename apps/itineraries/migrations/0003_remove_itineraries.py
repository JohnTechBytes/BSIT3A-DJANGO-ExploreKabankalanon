from django.db import migrations
from importlib import import_module


def recheck(apps, schema_editor):
    import_module("apps.core.migrations.0002_legacy_removal_guard").guard(apps, schema_editor)

class Migration(migrations.Migration):
    dependencies = [('itineraries', '0002_initial'), ('core', '0002_legacy_removal_guard')]
    operations = [migrations.RunPython(recheck, migrations.RunPython.noop), migrations.DeleteModel(name='ItineraryStop'), migrations.DeleteModel(name='Itinerary')]
