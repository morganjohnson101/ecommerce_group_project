# Generated by Django 3.1.7 on 2021-04-29 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nike_run_app', '0005_auto_20210428_2255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoe',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
