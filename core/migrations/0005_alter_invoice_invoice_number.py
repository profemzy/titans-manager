# Generated by Django 5.1.5 on 2025-01-30 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_invoice_invoice_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(editable=False, max_length=50, unique=True),
        ),
    ]
