# Generated by Django 3.1 on 2024-03-18 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authy', '0012_profile_phone_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='sec_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
