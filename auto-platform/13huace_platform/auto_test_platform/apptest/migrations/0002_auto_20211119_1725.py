# Generated by Django 3.2.4 on 2021-11-19 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apptest', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appcase',
            old_name='WebCase',
            new_name='AppCase',
        ),
        migrations.RenameField(
            model_name='appcase',
            old_name='SeleniumHubServer',
            new_name='Device',
        ),
    ]
