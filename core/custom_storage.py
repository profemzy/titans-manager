from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureReceiptStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_RECEIPT_CONTAINER
    expiration_secs = settings.AZURE_EXPIRATION_SECS

    def get_valid_name(self, name):
        """
        Returns a filename that's allowed in Azure Blob Storage.
        Removes potentially problematic characters.
        """
        import re
        s = str(name).strip().replace(' ', '_')
        s = re.sub(r'[^a-zA-Z0-9._-]', '', s)
        return s

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system.
        If the filename exists, it will append a timestamp.
        """
        from datetime import datetime
        import os

        if self.exists(name):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name = os.path.join(dir_name, f'{file_root}_{timestamp}{file_ext}')
        return name
