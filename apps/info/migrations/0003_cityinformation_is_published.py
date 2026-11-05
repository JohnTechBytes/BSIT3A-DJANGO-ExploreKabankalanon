from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cityinformation",
            name="is_published",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text=(
                    "Only published entries are visible on the public City "
                    "Information page."
                ),
            ),
        ),
    ]
