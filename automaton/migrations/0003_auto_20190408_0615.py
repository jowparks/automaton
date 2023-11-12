# Generated by Django 2.1.7 on 2019-04-08 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automaton', '0002_auto_20190405_0537'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestor',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='requestor',
            name='number',
            field=models.CharField(db_index=True, max_length=15, unique=True),
        ),
    ]