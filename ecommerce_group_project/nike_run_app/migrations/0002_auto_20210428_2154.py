# Generated by Django 2.2 on 2021-04-29 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nike_run_app', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.RemoveField(
            model_name='shoe',
            name='buyer',
        ),
        migrations.AddField(
            model_name='shoe',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='shoe',
            name='image_path',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]