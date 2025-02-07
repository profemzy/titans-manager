from django.db import migrations, models

import core.custom_storage
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expense",
            name="receipt",
            field=models.FileField(
                blank=True,
                null=True,
                storage=core.custom_storage.AzureReceiptStorage(),
                upload_to=core.models.Expense.receipt_upload_path,
            ),
        ),
    ]
