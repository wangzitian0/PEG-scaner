from django.conf import settings
from django.db import migrations, models


def table_name():
    prefix = getattr(settings, 'DB_TABLE_PREFIX', 'dev_')
    return f'{prefix}tracking'


class Migration(migrations.Migration):

    dependencies = [
        ('stock_research', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': table_name(),
                'ordering': ['-created_at'],
                'verbose_name': 'Tracking Record',
                'verbose_name_plural': 'Tracking Records',
            },
        ),
    ]
