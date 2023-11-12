# Generated by Django 2.2 on 2019-04-05 04:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Requestor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(db_index=True, max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OmbiRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('movie', 'Movie'), ('tv_show', 'TV Show'), ('choice', 'Choice'), ('unknown', 'Unknown')], max_length=50)),
                ('request_body', models.TextField()),
                ('provided_options', models.TextField()),
                ('status', models.CharField(choices=[('complete', 'Complete'), ('awaiting_response', 'Awaiting Response'), ('failed', 'Failed')], default='awaiting_response', max_length=20)),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='automaton.Requestor')),
            ],
        ),
    ]
