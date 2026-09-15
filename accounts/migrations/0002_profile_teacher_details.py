from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial"), ("academics", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="teaching_position",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="profile",
            name="teaching_subjects",
            field=models.ManyToManyField(
                blank=True, related_name="teachers", to="academics.subject"
            ),
        ),
    ]
