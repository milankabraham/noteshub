# Generated by Django 3.1 on 2024-03-15 06:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authy', '0008_auto_20240315_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='preview_image',
        ),
    ]