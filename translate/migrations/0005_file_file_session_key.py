# Generated by Django 2.1.7 on 2019-04-02 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0004_auto_20190327_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_session_key',
            field=models.CharField(default='', max_length=40, verbose_name='Session Key'),
        ),
    ]
