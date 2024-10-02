# Generated by Django 4.2.15 on 2024-09-22 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0014_donation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
