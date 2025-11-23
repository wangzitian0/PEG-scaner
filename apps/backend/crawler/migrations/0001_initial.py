from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CrawlerJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Human readable job name', max_length=255)),
                ('symbol', models.CharField(help_text='Stock symbol (e.g. AAPL)', max_length=16)),
                ('target_url', models.URLField(blank=True, help_text='Entry point for the crawler', null=True)),
                ('schedule_cron', models.CharField(blank=True, help_text='Cron expression used by the scheduler (optional)', max_length=64)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('last_run_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-updated_at'],
                'verbose_name': 'Crawler Job',
                'verbose_name_plural': 'Crawler Jobs',
            },
        ),
    ]
