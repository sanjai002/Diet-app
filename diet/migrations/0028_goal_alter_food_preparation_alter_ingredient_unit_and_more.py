# Generated by Django 4.1 on 2024-03-01 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diet', '0027_userdetails_bmi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='food',
            name='Preparation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='food',
            name='goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='diet.goal'),
        ),
        migrations.AddField(
            model_name='userdetails',
            name='Goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='diet.goal'),
        ),
    ]