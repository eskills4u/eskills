# Generated by Django 3.2.5 on 2021-07-08 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210709_0217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='register_table',
            name='contact_number',
        ),
    ]
