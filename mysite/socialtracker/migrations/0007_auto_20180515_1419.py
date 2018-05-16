# Generated by Django 2.0.4 on 2018-05-15 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialtracker', '0006_auto_20180515_0138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fackbookprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='githubprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='twitterprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='FackbookProfile',
        ),
        migrations.DeleteModel(
            name='GithubProfile',
        ),
        migrations.DeleteModel(
            name='TwitterProfile',
        ),
        migrations.DeleteModel(
            name='UserInfo',
        ),
    ]
