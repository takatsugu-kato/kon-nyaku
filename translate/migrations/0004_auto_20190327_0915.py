# Generated by Django 2.1.7 on 2019-03-27 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0003_file_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='source_lang',
            field=models.CharField(default='', max_length=8, verbose_name='ソース言語'),
        ),
        migrations.AddField(
            model_name='file',
            name='target_lang',
            field=models.CharField(default='', max_length=8, verbose_name='ターゲット言語'),
        ),
        migrations.AlterField(
            model_name='file',
            name='document',
            field=models.FileField(upload_to='media/', verbose_name='ファイル'),
        ),
    ]