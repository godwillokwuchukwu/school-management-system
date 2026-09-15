from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("students", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="student",
            name="parents",
            field=models.ManyToManyField(
                blank=True, related_name="children", to="accounts.profile"
            ),
        ),
    ]
