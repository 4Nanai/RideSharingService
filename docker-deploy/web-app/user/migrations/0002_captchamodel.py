# Generated by Django 5.1.4 on 2025-01-29 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaptchaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=100)),
                ('captcha', models.CharField(max_length=6)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
