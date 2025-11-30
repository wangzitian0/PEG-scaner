"""Initial migration for CMS Content models."""

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContentPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(help_text='URL-friendly identifier', unique=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField(help_text='Markdown or HTML content')),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('meta_title', models.CharField(blank=True, max_length=200)),
                ('meta_description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Content Page',
                'verbose_name_plural': 'Content Pages',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('level', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')], default='info', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_dismissible', models.BooleanField(default=True)),
                ('show_on_pages', models.CharField(blank=True, help_text='Comma-separated list of page paths, or empty for all pages', max_length=500)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'ordering': ['-start_date'],
            },
        ),
    ]

