# Generated by Django 4.1.3 on 2022-11-12 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_bookreservation_returned_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookreservation',
            name='due_back',
            field=models.DateField(blank=True, null=True),
        ),
    ]