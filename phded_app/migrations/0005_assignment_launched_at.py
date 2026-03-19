from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phded_app', '0004_studentassignmentattempt_studentanswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='launched_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
