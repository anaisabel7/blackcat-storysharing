# Generated by Django 2.0.3 on 2018-06-26 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storysharing', '0009_auto_20180612_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='shareable',
            field=models.BooleanField(default=False),
        ),
    ]
