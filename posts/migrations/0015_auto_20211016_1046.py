# Generated by Django 2.2.6 on 2021-10-16 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Добавте картинку', null=True, upload_to='posts/'),
        ),
    ]
