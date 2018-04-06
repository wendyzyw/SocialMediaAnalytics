# Generated by Django 2.0.3 on 2018-04-05 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_analytics', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_image_url',
            field=models.URLField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='oauth_token',
            field=models.CharField(blank=True, editable=False, max_length=200, null=True),
        ),
    ]
