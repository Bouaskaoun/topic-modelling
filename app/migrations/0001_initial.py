# Generated by Django 4.1.4 on 2022-12-08 21:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Untitled', max_length=255)),
                ('cleaned', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DataRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.data')),
            ],
        ),
    ]
