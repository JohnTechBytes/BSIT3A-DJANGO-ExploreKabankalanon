from django.db import migrations, models


def publish_existing_entries(apps, schema_editor):
    """Keep the entries that were public before the publish flag existed.

    Until this migration the public City Information page showed every row.
    Adding ``is_published`` with a default of ``False`` would silently empty
    that page, so the existing rows are published here. Staff can unpublish
    any of them again from the administrative panel.
    """
    CityInformation = apps.get_model("info", "CityInformation")
    CityInformation.objects.all().update(is_published=True)


def unpublish_existing_entries(apps, schema_editor):
    CityInformation = apps.get_model("info", "CityInformation")
    CityInformation.objects.all().update(is_published=False)


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0003_cityinformation_is_published"),
    ]

    operations = [
        migrations.AddField(
            model_name="cityinformation",
            name="photo_credit",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Credit line for the thumbnail, e.g. "
                    "'Photo: Juan Dela Cruz / Wikimedia Commons (CC BY-SA 4.0)'."
                ),
                max_length=500,
            ),
        ),
        migrations.RunPython(
            publish_existing_entries,
            unpublish_existing_entries,
        ),
    ]
