# Generated by Django 3.2.5 on 2021-07-09 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_add_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_course',
            name='course_image',
            field=models.ImageField(upload_to='courses/%Y/%m/%d'),
        ),
    ]
