import base64
import os
from django.conf import settings
from storages.backends.azure_storage import AzureStorage
from azure.storage.blob._shared.authentication import SharedKeyCredentialPolicy


class AzureReceiptStorage(AzureStorage):
    def __init__(self):
        super().__init__()
        # Ensure the account key is properly padded for base64
        if hasattr(settings, 'AZURE_ACCOUNT_KEY'):
            # Add padding if needed
            key = settings.AZURE_ACCOUNT_KEY
            padding = 4 - (len(key) % 4)
            if padding != 4:
                key = key + ('=' * padding)
            self.account_key = key

    account_name = settings.AZURE_ACCOUNT_NAME
    azure_container = settings.AZURE_RECEIPT_CONTAINER
    expiration_secs = getattr(settings, 'AZURE_EXPIRATION_SECS', 60 * 60 * 24)  # Default 24 hours

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

        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)

        while self.exists(name):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            proposed_name = os.path.join(dir_name, f'{file_root}_{timestamp}{file_ext}')

            if max_length:
                # Calculate maximum length for file_root
                available_length = max_length - len(dir_name) - len(file_ext) - 2  # -2 for separators
                if available_length > 0:
                    truncated_name = f'{file_root}_{timestamp}'[:available_length]
                    name = os.path.join(dir_name, f'{truncated_name}{file_ext}')
                else:
                    # If max_length is too restrictive, just return the truncated original
                    return name[:max_length] if max_length else name
            else:
                name = proposed_name

        return name
