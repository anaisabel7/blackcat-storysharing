# Generated by Django 2.0.3 on 2018-06-12 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storysharing', '0008_remove_story_writers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='story',
            old_name='writers_through',
            new_name='writers',
        ),
    ]
